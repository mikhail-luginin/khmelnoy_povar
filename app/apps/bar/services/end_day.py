from apps.bar.models import Money
from apps.bar.services.bar_info import get_full_information_of_day
from apps.iiko.services.storage import StorageService

from core.time import today_date
from core import total_values

from django.contrib import messages
from django.shortcuts import redirect


def complete_day(request):
    sum_cash_end_day = request.POST.get('sum_cash_end_day')
    code = request.GET.get('code')

    storage = StorageService().storage_get(code=code)
    information_of_day = get_full_information_of_day(today_date(), storage)

    try:
        row = Money.objects.get(date_at=today_date(), storage=storage)
    except Money.DoesNotExist:
        messages.error(request, 'Смена в CRM не была открыта :(')
        return redirect('/bar/end_day?code=' + code)

    calculated = int(sum_cash_end_day) - information_of_day["total_cash"] - \
                 information_of_day["expenses_nal"] - information_of_day["salary_prepayment"] - \
                 information_of_day['salary_month'] - information_of_day["payout"] + information_of_day["payin"]
    difference = int(sum_cash_end_day) - calculated

    row.total_day = information_of_day["total_day"]
    row.total_bn = information_of_day["total_bn"]
    row.total_cash = information_of_day["total_cash"]
    row.total_market = information_of_day["yandex"] + information_of_day["delivery"]
    row.total_expenses = total_values.get_total_expenses_by_date_and_storage(row.date_at, row.storage, is_bn=False)
    row.total_salary = total_values.get_total_salary_by_date_and_storage(row.date_at, row.storage, 1) \
                       + total_values.get_total_salary_by_date_and_storage(row.date_at, row.storage, 1)
    row.total_payin = total_values.get_total_payin_by_date_and_storage(row.date_at, row.storage)
    row.total_payout = total_values.get_total_payout_by_date_and_storage(row.date_at, row.storage)
    row.sum_cash_end_day = sum_cash_end_day
    row.calculated = calculated
    row.difference = difference
    row.save()

    messages.success(request, 'Остаток в кассе успешно заполнен :)')
    return redirect('/bar/end_day?code=' + code)
