from django.conf import settings
from django.db.models import Sum

from apps.lk.models import Fine
from config.celery import app

from core.telegram import send_message_to_telegram
from core.time import today_datetime

from global_services.salary import SalaryService


from apps.bar.models import Timetable


@app.task
def add_percent_and_premium_to_timetable(date_at: str, storage_id: int) -> None:
    try:
        timetable_objects = Timetable.objects.filter(date_at=date_at, storage_id=storage_id)
    except Timetable.DoesNotExist:
        send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, f'[Celery task add_percent_and_premium_to_timetable {today_datetime()}]'
                                                                       f' Запись не найдена.')
        return None

    for timetable in timetable_objects:
        money_data = SalaryService().calculate_prepayment_salary_by_timetable_object(timetable)
        percent = money_data['percent']
        premium = money_data['premium']

        timetable.percent = percent
        timetable.premium = premium

        try:
            fine = Fine.objects.get(date_at=timetable.date_at, employee_id=timetable.employee_id)
        except Fine.DoesNotExist:
            fine = None

        if fine:
            timetable.fine = fine.sum
            timetable.fine_reason_id = fine.reason_id
        timetable.save()
