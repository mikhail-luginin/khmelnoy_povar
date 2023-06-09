#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from django.conf import settings
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import redirect

from apps.bar.models import Pays
from apps.iiko.models import Storage
from apps.lk.models import Expense
from core.logs import create_log
from core.services import catalog_service
from core.services import storage_service, expenses_service
from core.utils.time import today_date


class ExpensesPageService:

    def get_expenses_today(self, storage: Storage) -> list[Expense]:
        return Expense.objects \
            .filter(storage=storage, date_at=today_date()) \
            .exclude(expense_type__name=settings.SALARY_CATEGORY) \
            .exclude(writer__contains='акупщик')

    def get_sum_expenses_today(self, storage: Storage) -> dict[str, int]:
        data = {
            "bn": Expense.objects
                  .filter(storage=storage,
                          date_at=today_date(),
                          expense_source__name=settings.PAYMENT_TYPE_BN)
                  .exclude(expense_type__name=settings.SALARY_CATEGORY)
                  .exclude(writer__contains='акупщик')
                  .aggregate(total_sum=Sum('sum'))['total_sum'] or 0,
            "nal": Expense.objects
                  .filter(storage=storage,
                          date_at=today_date(),
                          expense_source__name=settings.PAYMENT_TYPE_NAL)
                  .exclude(expense_type__name=settings.SALARY_CATEGORY)
                  .exclude(writer__contains='акупщик')
                  .aggregate(total_sum=Sum('sum'))['total_sum'] or 0
        }

        return data

    def create_expense(self, request) -> redirect:
        code = request.GET.get('code')
        storage = storage_service.storage_get(code=code)

        expense_source = request.POST.get('expense-source')
        if not expense_source:
            messages.error(request, 'Выберите тип оплаты.')
            return redirect(request.META.get('HTTP_REFERER'))

        expense_source_object = catalog_service.get_catalog_by_id(expense_source)
        if expense_source_object is None:
            messages.error(request, 'Выбранный тип оплаты не указан.')
            return redirect(request.META.get('HTTP_REFERER'))

        for row in catalog_service.get_catalog_by_type(settings.EXPENSE_TYPE_CATEGORY):
            expense_sum = request.POST.get(f'sum[{row.id}]')
            if len(expense_sum) > 0:
                expense = expenses_service.create(date_at=today_date(), storage_id=storage.id,
                                                  expense_type_id=row.id, expense_source_id=expense_source_object.id,
                                                  payment_receiver='Не указан', expense_sum=expense_sum,
                                                  comment=request.POST.get(f'comment[{row.id}]'), writer_barmen=True)
                create_log(owner=f'CRM {storage.name}', entity=storage.name, row=expense,
                           action='create', additional_data='Расход создан')

        messages.success(request, f'Расход успешно добавлен :)')
        return redirect('/bar/expenses?code=' + code)

    def pays_create(self, request):
        code = request.GET.get('code')
        redirect_url = '/bar/expenses?code=' + code

        storage = storage_service.storage_get(code=code)

        oil_sum = request.POST.get('oil_sum')
        oil_comment = request.POST.get('oil_comment')

        purchaser_sum = request.POST.get('purchaser_sum')
        purchaser_comment = request.POST.get('purchaser_comment')

        danil_sum = request.POST.get('danil_sum')
        danil_comment = request.POST.get('danil_comment')

        if len(oil_sum) > 0:
            if not oil_comment:
                messages.error(request, 'Комментарий к внесению не указан.')
                return redirect(redirect_url)

            from_to_id = catalog_service.get_catalog_by_name(catalog_name='Масло -')
            if from_to_id:
                from_to_id = from_to_id.id

            Pays.objects.create(
                date_at=today_date(),
                storage=storage,
                type=1,
                from_to_id=from_to_id,
                sum=oil_sum,
                comment=oil_comment
            )

        if len(purchaser_sum) > 0:
            if not purchaser_comment:
                messages.error(request, 'Комментарий к изъятию закупщика не указан.')
                return redirect(redirect_url)

            from_to_id = catalog_service.get_catalog_by_name(catalog_name='Закупщик')
            if from_to_id:
                from_to_id = from_to_id.id

            Pays.objects.create(
                date_at=today_date(),
                storage=storage,
                type=2,
                from_to_id=from_to_id,
                sum=purchaser_sum,
                comment=purchaser_comment
            )

        if len(danil_sum) > 0:
            if not danil_comment:
                messages.error(request, 'Комментарий к изъятию Данила не указан.')
                return redirect(redirect_url)

            from_to_id = catalog_service.get_catalog_by_name(catalog_name='Данил')
            if from_to_id:
                from_to_id = from_to_id.id

            Pays.objects.create(
                date_at=today_date(),
                storage=storage,
                type=2,
                from_to_id=from_to_id,
                sum=danil_sum,
                comment=danil_comment
            )

        messages.success(request, 'Запись успешно добавлена.')
        return redirect(redirect_url)
