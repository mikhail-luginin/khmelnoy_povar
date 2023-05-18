from django.db.models import Sum

from apps.bar.models import Pays
from apps.bar.services.bar_info import get_main_barmen

from apps.iiko.models import Storage
from apps.iiko.services.storage import StorageService

from apps.lk.models import Expense, Catalog
from apps.lk.services.catalog import CatalogService

from core.time import today_date
from core.logs import create_log

from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings


class ExpensesPageService:

    def get_expenses_today(self, storage: Storage) -> list[Expense]:
        return Expense.objects \
            .filter(storage=storage, date_at=today_date()) \
            .exclude(expense_type__name=settings.SALARY_CATEGORY)

    def get_sum_expenses_today(self, storage: Storage) -> dict[str, int]:
        data = {
            "bn": Expense.objects.filter(storage=storage,
                                         date_at=today_date(),
                                         expense_source__name=settings.PAYMENT_TYPE_BN).aggregate(total_sum=Sum('sum'))['total_sum'] or 0,
            "nal": Expense.objects.filter(storage=storage,
                                         date_at=today_date(),
                                         expense_source__name=settings.PAYMENT_TYPE_NAL).aggregate(total_sum=Sum('sum'))['total_sum'] or 0
        }

        return data

    def create_expense(self, request) -> redirect:
        code = request.GET.get('code')
        storage = StorageService().storage_get(code=code)
        barmen = get_main_barmen(today_date(), storage)

        expense_source = request.POST.get('expense-source')
        if not expense_source:
            messages.error(request, 'Выберите тип оплаты.')
            return redirect(request.META.get('HTTP_REFERER'))

        try:
            expense_source_object = CatalogService().get_catalog_by_id(expense_source)
        except Catalog.DoesNotExist:
            messages.error(request, 'Выбранный тип оплаты не указан.')
            return redirect(request.META.get('HTTP_REFERER'))

        for row in CatalogService().get_catalog_by_type(settings.EXPENSE_TYPE_CATEGORY):
            expense_sum = request.POST.get(f'sum[{row.id}]')
            if len(expense_sum) > 0:
                Expense.objects.create(
                    writer=barmen.fio if barmen else 'Основной бармен не указан',
                    date_at=today_date(),
                    storage=storage,
                    expense_type=row,
                    expense_source=expense_source_object,
                    payment_receiver='Не указан',
                    sum=expense_sum,
                    comment=request.POST.get(f'comment[{row.id}]')
                )
                create_log(barmen if type(barmen) is str else barmen.fio, request.path, 'Добавление расхода',
                           comment=storage.name, is_bar=True)

        messages.success(request, f'Расход успешно добавлен :)')
        return redirect('/bar/expenses?code=' + code)

    def pays_create(self, request):
        code = request.GET.get('code')
        redirect_url = '/bar/expenses?code=' + code

        storage = StorageService().storage_get(code=code)

        oil_sum = request.POST.get('oil_sum')
        oil_comment = request.POST.get('oil_comment')

        purchaser_sum = request.POST.get('purchaser_sum')
        purchaser_comment = request.POST.get('purchaser_comment')

        if len(oil_sum) > 0:
            if not oil_comment:
                messages.error(request, 'Комментарий к внесению не указан.')
                return redirect(redirect_url)

            Pays.objects.create(
                date_at=today_date(),
                storage=storage,
                type=5,
                sum=oil_sum,
                comment=oil_comment
            )

        if len(purchaser_sum) > 0:
            if not purchaser_comment:
                messages.error(request, 'Комментарий к изъятию закупщика не указан.')
                return redirect(redirect_url)

            Pays.objects.create(
                date_at=today_date(),
                storage=storage,
                type=4,
                sum=purchaser_sum,
                comment=purchaser_comment
            )

        messages.success(request, 'Запись успешно добавлена.')
        return redirect(redirect_url)
