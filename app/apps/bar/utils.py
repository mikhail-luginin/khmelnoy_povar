#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

import datetime
import xml.etree.ElementTree as ET

from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from apps.bar.models import TovarRequest, Arrival
from apps.iiko.models import Product, Category, Storage
from apps.lk.models import Expense, Catalog
from core.logs import create_log
from core.services import catalog_service, supplier_service
from core.services import storage_service, bar_service
from core.services.api.iiko import IikoService
from core.services.bar_service import get_setting_by_storage_id
from core.utils.payment_types import get_bn_category, get_nal_category
from core.utils.telegram import send_message_to_telegram
from core.utils.time import today_date, monthdelta, get_current_time, get_months
from .services.bar_info import get_bar, get_main_barmen


class BaseView(View):
    template_name = None

    def get_context_data(self, request, **kwargs) -> dict:
        code = request.GET.get('code')
        bar = get_bar(code=code)

        context = dict()

        context['code'] = code
        context['bar'] = bar
        if bar is not None:
            context['setting'] = get_setting_by_storage_id(storage_id=bar.id)
        context['date'] = today_date()

        context.update(**kwargs)

        return context

    def get(self, request):
        context = self.get_context_data(request)

        if request.path != '/bar/' and request.path != '/bar/employee':
            storage = context.get('bar')
            if storage:
                storage_id = storage.id
                main_barmen = bar_service.get_main_barmen_on_storage_by_date(date_at=today_date(),
                                                                             storage_id=storage_id)
                if main_barmen is None:
                    messages.error(request, 'Укажите основного бармена.')
                    return redirect(f'/bar?code={context.get("code")}')

        return render(request, self.template_name, context=context)


class ObjectDeleteMixin(BaseView):
    model = None

    def get(self, request):
        try:
            row = self.model.objects.get(id=request.GET.get('id'))

            if type(row).__name__ == 'Timetable':
                create_log(owner=f'CRM {row.storage.name}', entity=row.employee.fio, row=row,
                           action='delete', additional_data='Удален со смены')
            else:
                create_log(owner=f'CRM {row.storage.name}', entity=row.storage.name, row=row,
                           action='delete', additional_data='Запись удалена')
            row.delete()
        except self.model.DoesNotExist:
            messages.error(request, 'Данная запись не найдена.')
            return redirect(request.META.get('HTTP_REFERER'))

        messages.success(request, 'Запись успешно удалена.')
        return redirect(request.META.get('HTTP_REFERER'))


class ProductsMovementMixin(BaseView):
    category = None
    model = None

    def get_category_or_404(self):
        return get_object_or_404(Category, name=self.category)

    def get_category_products(self):
        category = self.get_category_or_404()
        return Product.objects.filter(category=category)

    def get(self, request):
        try:
            category = self.get_category_or_404()
        except Http404:
            messages.error(request,
                           f'Категория продукта "{self.category}" не найдена :( \n Сообщите в телеграм: @AleksLuginin')
            return redirect(request.META.get('HTTP_REFERER'))

        return render(
            request,
            self.template_name,
            context=self.get_context_data(
                request,
                products=self.get_category_products(),
                category=self.category,
                rows=self.model.objects.filter(date_at=today_date(),
                                               storage=storage_service.storage_get(code=request.GET.get('code')),
                                               product__category=category),
            )
        )


class TovarRequestMixin(ProductsMovementMixin):
    template_name = 'bar/tovar_requests.html'
    model = TovarRequest

    def post(self, request):
        context = self.get_context_data(request)

        for product in self.get_category_products():
            if request.POST.get(f'{product.id}') is not None:
                row = self.model.objects.create(
                    date_at=today_date(),
                    storage=storage_service.storage_get(code=request.GET.get('code')),
                    product=product,
                    product_amount=product.minimal if product.minimal is not None else 1,
                    product_main_unit=product.main_unit,
                    supplier=product.supplier
                )
                create_log(owner=f'CRM {context.get("bar").name}', entity=product.name, row=row,
                           action='create', additional_data=f'Заявка пополнена ({product.name})')

        messages.success(request, 'Заявка пополнена.')
        return redirect(request.META.get('HTTP_REFERER'))


class ArrivalMixin(ProductsMovementMixin):
    template_name = 'bar/arrivals.html'
    model = Arrival

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update({
            "suppliers": supplier_service.suppliers_all()
        })

        return context

    def post(self, request):
        invoice_number = request.POST.get('invoice-number')
        product_id = request.POST.get('product-id')
        product_id = product_id if product_id != '' else -1
        amount = request.POST.get('amount')
        invoice_sum = request.POST.get('sum')
        payment_type = request.POST.get('payment-type')

        storage = storage_service.storage_get(code=request.GET.get('code'))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            messages.error(request, 'Указанный продукт не найден в базе :(')
            return redirect(request.META.get('HTTP_REFERER'))

        arrival = self.model(
            date_at=today_date(),
            storage=storage,
            num=invoice_number,
            product=product,
            supplier=product.supplier,
            amount=amount,
            sum=invoice_sum
        )

        if payment_type.lower() != 'неоплачено':
            arrival.type = 2
            arrival.payment_date = today_date()
            main_barmen = get_main_barmen(today_date(), storage) if type(get_main_barmen(today_date(), storage)) is str \
                else get_main_barmen(today_date(), storage).fio

            try:
                expense_type = catalog_service.get_catalog_by_name(settings.TOVAR_ARRIVAL_CATEGORY)
            except Catalog.DoesNotExist:
                messages.error(request, 'Категория для типа расхода не найдена.')
                return redirect(request.META.get('HTTP_REFERER'))

            expense = Expense(
                writer=main_barmen,
                date_at=today_date(),
                storage=storage,
                expense_type=expense_type,
                payment_receiver=product.supplier.name if product.supplier else None,
                sum=invoice_sum,
                comment=f'{product.name} ({invoice_number})'
            )
            match payment_type:
                case 'nal':
                    try:
                        arrival.payment_type = get_nal_category()
                        expense.expense_source = get_nal_category()
                    except Http404:
                        messages.error(request, 'Категория "наличные" не найдена :(')
                        return redirect(request.META.get('HTTP_REFERER'))
                case 'bn':
                    try:
                        arrival.payment_type = get_bn_category()
                        expense.expense_source = get_bn_category()
                    except Http404:
                        messages.error(request, 'Категория "безнал" не найдена :(')
                        return redirect(request.META.get('HTTP_REFERER'))
                case _:
                    messages.error(request, 'Вы не выбрали тип оплаты.')
                    return redirect(request.META.get('HTTP_REFERER'))
            expense.save()

        arrival.save()
        create_log(owner=f'CRM {storage.name}', entity=product.name, row=arrival,
                   action='create', additional_data=f'Приход товара заполнен ({product.name})')

        messages.success(request, 'Поступление успешно записано :)')
        return redirect(request.META.get('HTTP_REFERER'))


class InventoryMixin(BaseView):
    category_name = None
    template_name = 'bar/inventory.html'

    def get_category(self):
        try:
            return Category.objects.get(name=self.category_name)
        except Category.DoesNotExist:
            return None

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context['products'] = Product.objects.filter(category=self.get_category())
        context['category'] = self.category_name

        return context

    def post(self, request):
        storage = storage_service.storage_get(code=request.GET.get('code'))

        xml = IikoService().check_inventory(storage.storage_id, self.category_name)
        items = ET.fromstring(xml)
        row = dict()
        message_header = f'Дата: {today_date()}\nЗаведение: {storage.name}\n\n'
        message_body = ''
        for item in items.findall('items/item'):
            name = None
            code = None
            for product in item.findall('product'):
                name = product.find('name').text
                code = product.find('code').text
                if code and len(code) > 0:
                    code = int(code)
                else:
                    continue
            expected_amount = item.find('expectedAmount').text
            count = request.POST.get(str(code))
            if len(count) == 0:
                count = 0
            difference = int(count) - int(round(float(expected_amount)))
            row[name] = {'fact': count, 'iiko': int(round(float(expected_amount))), 'difference': difference}
            if difference < 0:
                message_body += f'{name}: [разница: {difference}]\n'
        if message_body != '':
            message = message_header + message_body
            send_message_to_telegram(chat_id='-619967297', message=message)

        return render(request, 'bar/inventory_table.html', self.get_context_data(request, rows=row))


class DataLogsMixin(BaseView):
    model = None
    type = None  # type = 1 по дням, type = 2 по месяцам

    def _prepare_context(self, obj: str | None) -> dict:
        context = dict()

        if obj and obj != '0':
            obj = int(obj)
            context['obj'] = obj
            context['previous'] = obj - 1
            context['next'] = obj + 1
            context['is_current'] = True
        else:
            context['previous'] = -1
            context['is_current'] = False

        return context

    def _prepare_rows(self, storage: Storage, obj: int | None) -> tuple[list, str]:
        current_date = get_current_time()

        filter_args = None
        match self.type:
            case 1:
                day = (current_date + datetime.timedelta(days=obj)) if obj else current_date.day
                filter_args = {"date_at__day": day if type(day) is int else day.day,
                               "date_at__month": day.month if obj else current_date.month}
            case 2:
                obj = monthdelta(current_date, obj).month if obj else current_date.month
                filter_args = {"date_at__month": obj}

        day = filter_args.get('date_at__day')
        month = filter_args.get('date_at__month')

        date = f"{get_months(month) if month else get_months(current_date.month)} {day if day else current_date.day}"

        return [row for row in self.model.objects.filter(**filter_args, storage=storage)], date

    def get_context_data(self, request, **kwargs) -> dict:
        context = super().get_context_data(request, **kwargs)
        context.update(self._prepare_context(obj=request.GET.get('date')))

        prepare_rows = self._prepare_rows(storage=context.get('bar'), obj=context.get('obj'))

        if type(prepare_rows) is tuple:
            context['rows'] = prepare_rows[0]
            context['date'] = prepare_rows[1]
        return context
