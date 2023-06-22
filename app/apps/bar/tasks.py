from django.conf import settings

from apps.bar.models import Timetable
from apps.lk.models import Fine
from config.celery import app
from core.telegram import send_message_to_telegram
from core.time import today_datetime
from global_services.salary import SalaryService


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

        fine = 0
        for row in Fine.objects.filter(date_at=timetable.date_at, employee_id=timetable.employee_id):
            fine += row.sum

        timetable.fine = fine
        timetable.save()
