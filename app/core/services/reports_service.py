from django.db.models import Sum
from django.conf import settings

from apps.bar.models import Money, Salary
from apps.lk.models import Expense
from core.services import storage_service, catalog_service
from core.utils.time import get_months, get_current_time

from calendar import monthrange


class ReportsService:

    def _update_incomes_expenses_report(self, storage_id: int) -> dict[str, list]:
        data = {
            "incomes": [],
            "expenses": []
        }
        for month in get_months().keys():
            total_money = Money.objects.filter(
                date_at__month=month,
                date_at__year=get_current_time().year,
                storage_id=storage_id
            ).aggregate(total_money=Sum('total_day'))['total_money']
            data['incomes'].append(round(total_money) if total_money else 0)
            expenses = Expense.objects.filter(
                date_at__month=month,
                date_at__year=get_current_time().year,
                storage_id=storage_id
            ).aggregate(total_money=Sum('sum'))['total_money']
            salaries = Salary.objects.filter(
                date_at__month=month,
                date_at__year=get_current_time().year,
                storage_id=storage_id
            ).aggregate(total_sum=Sum('oklad') + Sum('percent') + Sum('premium'))['total_sum']
            data['expenses'].append(round(expenses) if expenses else 0 + round(salaries) if salaries else 0)

        return data

    def update_money_reports(self):
        data = []
        for storage in storage_service.storages_all():
            incomes_expenses_data = self._update_incomes_expenses_report(storage_id=storage.id)

            storage = {
                "storage_id": storage.id,
                "incomes_data": incomes_expenses_data.get('incomes'),
                "expenses_data": incomes_expenses_data.get('expenses')
            }
            data.append(storage)

        return data

    def _update_expense_types_by_storages_report(self, expense_type_id: int, month: int,
                                                 year: int, days: int) -> list[dict[str, list[int]]]:
        data = []

        for storage in storage_service.storages_all():
            storage_dict = {"name": storage.name, "data": []}
            for day in range(days):
                expenses = Expense.objects.filter(
                    date_at__year=year, date_at__month=month, date_at__day=day+1,
                    storage_id=storage.id, expense_type_id=expense_type_id
                ).aggregate(Sum('sum'))['sum__sum']
                storage_dict['data'].append(round(expenses) if expenses else 0)
            data.append(storage_dict)

        return data


    def update_expense_types_by_storages_reports(self, year: int, month_id: int):
        days = monthrange(year=year, month=month_id)[1]

        data = {"year": year, "month": month_id,
                "days_array": [day+1 for day in range(days)], "expenses": {}}
        for expense_type in catalog_service.get_catalog_by_type(settings.EXPENSE_TYPE_CATEGORY):
            expense_type_data = self._update_expense_types_by_storages_report(
                expense_type_id=expense_type.id, month=month_id, year=year, days=days
            )
            data["expenses"][expense_type.id] = {"name": expense_type.name, "sum": expense_type_data}

        return data
