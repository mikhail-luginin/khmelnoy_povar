from django.conf import settings

from apps.bar.services.index import HomePageService
from config.celery import app

from core.services import storage_service, money_service
from core.utils.telegram import send_message_to_telegram
from core.utils.time import today_datetime, get_current_time, today_date
from core.services.salary_service import SalaryService

from apps.bar.models import Timetable
from apps.lk.models import Fine

import datetime


@app.task
def add_percent_and_premium_to_timetable(date_at: str, storage_id: int) -> None:
    try:
        timetable_objects = Timetable.objects.filter(date_at=date_at, storage_id=storage_id)
    except Timetable.DoesNotExist:
        send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS,
                                 f'[Celery task add_percent_and_premium_to_timetable {today_datetime()}]'
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


@app.task
def create_money_records():
    for storage in storage_service.storages_all():
        yesterday_money_evening_cashbox = HomePageService().evening_cashbox_previous_day(storage=storage)
        if money_service.money_get(date_at=today_date(), storage_id=storage.id) is None:
            money_service.create_money_record(date_at=today_date(), storage_id=storage.id,
                                              sum_cash_morning=yesterday_money_evening_cashbox)
