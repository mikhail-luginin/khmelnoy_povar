from apps.bar.models import Money, TovarRequest, Setting, Timetable
from apps.bar.services.bar_info import get_full_information_of_day
from apps.iiko.services.storage import StorageService
from core.telegram import send_message_to_telegram

from core.time import today_date
from core import total_values

from apps.bar.tasks import add_percent_and_premium_to_timetable

from django.contrib import messages
from django.shortcuts import redirect

from global_services.salary import SalaryService


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

    bar_setting = Setting.objects.get(storage=storage)

    calculated = int(row.sum_cash_morning) + information_of_day["total_cash"] - \
                 information_of_day["expenses_nal"] - information_of_day["salary_prepayment"] - \
                 information_of_day['salary_month'] - information_of_day["payout"] + information_of_day["payin"]
    difference = int(sum_cash_end_day) - calculated

    row.total_day = information_of_day["total_day"]
    row.total_bn = information_of_day["total_bn"]
    row.total_cash = information_of_day["total_cash"]
    row.total_market = information_of_day["yandex"] + information_of_day["delivery"]
    row.total_expenses = total_values.get_total_expenses_by_date_and_storage(row.storage, row.date_at, is_bn=False)
    row.total_salary = total_values.get_total_salary_by_date_and_storage(row.storage, row.date_at, 1) \
                       + total_values.get_total_salary_by_date_and_storage(row.storage, row.date_at, 1)
    row.total_payin = total_values.get_total_payin_by_date_and_storage(row.storage, row.date_at)
    row.total_payout = total_values.get_total_payout_by_date_and_storage(row.storage, row.date_at)
    row.sum_cash_end_day = sum_cash_end_day
    row.calculated = calculated
    row.difference = difference
    row.save()

    add_percent_and_premium_to_timetable.delay(today_date(), storage.id)
    messages.success(request, 'Остаток в кассе успешно заполнен :)')

    message = f'Дата: <b>{today_date()}</b>\nЗаведение: {storage.name}\n\n'

    tovar_request_message = message
    for tovar_request in TovarRequest.objects.filter(date_at=today_date(), storage_id=storage.id):
        tovar_request_message += f'{tovar_request.product.name}\n'
    send_message_to_telegram('-1001646808631', tovar_request_message)

    end_day_message = message
    end_day_message += 'Смена успешно закрыта. Отчет:\n\n'
    end_day_message += f'Выручка: <b>{row.total_day}</b>\nНаличные: {row.total_cash}\nБезнал: {row.total_bn}\n' \
                       f'Маркеты: {row.total_market}\n' \
                       f'Сумма для начисления процентов: {row.total_day - row.total_market}\n\n' \
                       f'Касса утро: {row.sum_cash_morning}\nРасходы (из кассы): {row.total_expenses}\n' \
                       f'Зарплаты: {row.total_salary}\n' \
                       f'Внесения: {row.total_payin}\nИзъятия: {row.total_payout}\n\n' \
                       f'Остаток наличных в кассе: {row.sum_cash_end_day}\nРасчетный остаток: {row.calculated}\n' \
                       f'Разница: <b>{row.difference}</b>\n\n' \
                       f'<b>Начисленная</b> зарплата:\n'
    for timetable in Timetable.objects.filter(date_at=today_date(), storage_id=row.storage_id):
        salary = SalaryService().calculate_prepayment_salary_by_timetable_object(timetable_object=timetable)
        end_day_message += f'{timetable.employee.fio} ({timetable.position.name}): <b>{salary["oklad"] + salary["percent"] + salary["premium"]}</b>\n'
    send_message_to_telegram(chat_id=bar_setting.tg_chat_id,
                             message=end_day_message)

    return redirect('/bar/end_day?code=' + code)
