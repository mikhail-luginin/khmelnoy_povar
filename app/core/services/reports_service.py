from django.db.models import Sum

from apps.bar.models import Money, Salary
from apps.lk.models import Expense
from core.services import storage_service
from core.utils.time import get_months, get_current_time


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
