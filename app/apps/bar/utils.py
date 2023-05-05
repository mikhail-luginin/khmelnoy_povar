from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.http import Http404
from django.conf import settings

from core.telegram import send_message_to_telegram

from apps.bar.models import TovarRequest, Arrival

from .services.bar_info import get_bar, get_main_barmen

from apps.iiko.models import Product, Category
from apps.iiko.services.api import IikoService
from apps.iiko.services.storage import StorageService

from core.time import today_date
from core.logs import create_log
from core.payment_types import get_bn_category, get_nal_category
import xml.etree.ElementTree as ET

from apps.lk.models import Expense, Catalog
from apps.lk.services.catalog import CatalogService


class BaseView(View):
    template_name = None

    def get_context_data(self, request, **kwargs) -> dict:
        code = request.GET.get('code')
        bar = get_bar(code=code)

        context = dict()

        context['code'] = code
        context['bar'] = bar
        context['date'] = today_date()

        context.update(**kwargs)

        return context

    def get(self, request):
        return render(request, self.template_name, self.get_context_data(request))


class ObjectDeleteMixin(BaseView):
    model = None

    def get(self, request):
        error = False
        try:
            row = self.model.objects.get(id=request.GET.get('id'))
            row.delete()
            today_main_barmen = get_main_barmen(today_date(), row.storage)
            username_for_logs = 'Основной бармен отсутствует' if not today_main_barmen else today_main_barmen.fio
            create_log(username_for_logs, request.path, f'Удаление записи в модели {str(self.model)}',
                       comment=row.storage.name, is_bar=True)
        except self.model.DoesNotExist:
            messages.error(request, 'Данная запись не найдена :(')
            error = True

        if error is False:
            messages.success(request, 'Запись успешно удалена :)')
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
                                               storage=StorageService().storage_get(code=request.GET.get('code')),
                                               product__category_id=category),
            )
        )


class TovarRequestMixin(ProductsMovementMixin):
    template_name = 'bar/tovar_requests.html'
    model = TovarRequest

    def post(self, request):
        for product in self.get_category_products():
            if request.POST.get(f'{product.id}') is not None:
                self.model.objects.create(
                    date_at=today_date(),
                    storage=StorageService().storage_get(code=request.GET.get('code')),
                    product=product,
                    product_amount=product.minimal if product.minimal is not None else 1,
                    product_main_unit=product.main_unit,
                    supplier=product.supplier
                )

        messages.success(request, 'Заявка пополнена :)')
        return redirect(request.META.get('HTTP_REFERER'))


class ArrivalMixin(ProductsMovementMixin):
    template_name = 'bar/arrivals.html'
    model = Arrival

    def post(self, request):
        invoice_number = request.POST.get('invoice-number')
        product_id = request.POST.get('product-id')
        product_id = product_id if product_id != '' else -1
        amount = request.POST.get('amount')
        invoice_sum = request.POST.get('sum')
        payment_type = request.POST.get('payment-type')

        storage = StorageService().storage_get(code=request.GET.get('code'))

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
                expense_type = CatalogService().get_catalog_by_type(settings.TOVAR_ARRIVAL_CATEGORY)
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
        storage = StorageService().storage_get(code=request.GET.get('code'))

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
            expected_amount = item.find('expectedAmount').text
            count = request.POST.get(code) if request.POST.get(code) != '' else '0'
            difference = int(count) - int(round(float(expected_amount)))
            row[name] = {'fact': count, 'iiko': int(round(float(expected_amount))), 'difference': difference}
            if difference < 0:
                message_body += f'{name}: [факт: {count}, iiko: {int(round(float(expected_amount)))}, difference: {difference}]\n'
        if message_body != '':
            message = message_header + message_body
            send_message_to_telegram(chat_id='-619967297', message=message)

        return render(request, 'bar/inventory_table.html', self.get_context_data(request, rows=row))
