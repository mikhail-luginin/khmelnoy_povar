from django.conf import settings

from apps.bar.services.index import HomePageService
from config.celery import app

from core.services import storage_service, money_service
from core.utils.telegram import send_message_to_telegram
from core.utils.time import today_datetime, today_date
from core.services.salary_service import SalaryService

from apps.bar.models import Timetable, Salary
from apps.lk.models import Fine


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


@app.task
def get_salary_prepayment_rows(storage_id: int) -> dict:
    data = {
        "rows": [],
        "total_sum": 0,
        "issued_sum": 0,
        "left_sum": 0
    }

    for timetable in Timetable.objects.filter(storage_id=storage_id, date_at=today_date()):
        row = {
            "oklad": 0,
            "percent": 0,
            "premium": 0
        }

        employee_money_information = SalaryService().calculate_prepayment_salary_by_timetable_object(
            timetable_object=timetable
        )
        percent = employee_money_information['percent']
        premium = employee_money_information['premium']

        salary = Salary.objects.filter(employee=timetable.employee, type=1, date_at=today_date()).first()
        is_accrued = True
        if salary is None:
            salary = None
            is_accrued = False

        row['employee_fio'] = timetable.employee.fio
        row['employee_code'] = timetable.employee.code
        row['employee_job'] = timetable.employee.job_place.name
        row['position_name'] = timetable.position.name
        row['is_accrued'] = is_accrued

        if is_accrued:
            row['oklad'] = salary.oklad
            row['percent'] = salary.percent
            row['premium'] = salary.premium
            data['issued_sum'] += salary.oklad + salary.percent + salary.premium
        else:
            if not timetable.position.args['is_trainee']:
                if timetable.position.args['is_called']:
                    if timetable.position.args['is_usil']:
                        row['oklad'] = timetable.employee.job_place.gain_shift_oklad_accrual
                    else:
                        row['oklad'] = timetable.employee.job_place.main_shift_oklad_accrual
                else:
                    if timetable.position.args['is_usil']:
                        row['oklad'] = timetable.employee.job_place.gain_shift_oklad_receiving
                    else:
                        row['oklad'] = timetable.employee.job_place.main_shift_oklad_receiving
                row['percent'] = percent if timetable.position.args['has_percent'] is True else 0
                row['premium'] = premium if timetable.position.args['is_called'] else 0

        row['has_percent'] = timetable.position.args['has_percent']
        row['has_premium'] = timetable.position.args['has_premium']
        data['total_sum'] += row['oklad'] + row['percent'] + row['premium']

        data['rows'].append(row)
        data['left_sum'] = data['total_sum'] - data['issued_sum']

    return data

