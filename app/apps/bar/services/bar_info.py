import datetime
import json
from typing import Type

from apps.bar.models import Timetable, Setting, Money
from core.services.api.iiko import IikoService
from apps.lk.models import Position, JobPlace, Employee
from apps.iiko.models import Storage, PaymentType

from core.utils import total_values
from core.utils.telegram import send_message_to_telegram
from core.utils.time import today_date, get_current_time

from django.conf import settings


def get_bar(code: str) -> Storage | None:
    try:
        return Storage.objects.get(code=code)
    except Storage.DoesNotExist:
        return None


def get_bar_settings(storage_id: Type[int] | int) -> Setting:
    return Setting.objects.filter(storage_id=storage_id).first()


def get_position_main_id(is_called: bool, job_name: str) -> int:
    job = JobPlace.objects.get(name=job_name)
    for position in Position.objects.all():
        if not position.args['is_usil'] and not position.args['is_trainee'] and position.args['is_called'] is is_called:
            if job in position.linked_jobs.all():
                return position.id


def get_main_barmen(date_at: str, storage: Storage) -> Employee | None:
    qs = Timetable.objects.filter(date_at=date_at,
                                storage=storage,
                                position_id__in=[
                                    get_position_main_id(False, 'Бармен'),
                                    get_position_main_id(True, 'Бармен')
                                ])
    if qs.exists():
        row = qs.first()
        return row.employee
    else:
        return None

def get_full_information_of_day_for_data_logs(days: str, storage: Storage):
    if not days:
        days = 0
    date = (get_current_time() + datetime.timedelta(days=int(days))).strftime('%Y-%m-%d')
    return get_full_information_of_day(date_at=date, storage=storage)


def get_full_information_of_day(date_at: str, storage: Storage) -> dict:
    money_record = Money.objects.filter(date_at=date_at, storage=storage).first()
    if money_record is None:
        return {"error": True}

    today = None
    sum_cash_morning = money_record.sum_cash_morning
    sum_cash_end_day = money_record.sum_cash_end_day
    calculated = money_record.calculated
    difference = money_record.difference

    if date_at == today_date():
        total_day = 0
        cash = 0
        cash_point = 0
        total_cashshifts = 0
        delivery = 0
        yandex = 0

        open_date = None
        close_date = None
        session_number = None

        json_data = json.loads(IikoService().get_cashshifts(date_at, date_at))
        for row in json_data:
            if row["pointOfSaleId"] == storage.point_of_sale:
                sales_by_department = json.loads(IikoService().get_sales_by_department(row["id"]))
                total_day += row["payOrders"]

                open_date = row["openDate"]
                if open_date is not None:
                    open_date = f'{open_date.split("T")[0]} {open_date.split("T")[1]}'
                close_date = row["closeDate"]
                if close_date is not None:
                    close_date = f'{close_date.split("T")[0]} {close_date.split("T")[1]}'

                session_number = row["sessionNumber"]

                payment_types = {}
                for payment_type in PaymentType.objects.all():
                    payment_types[payment_type.payment_id] = payment_type.name

                for sale in sales_by_department['cashlessRecords']:
                    pm_filter = payment_types.get(sale["info"]["paymentTypeId"])
                    if pm_filter:
                        if 'elivery' in pm_filter:
                            delivery += int(sale["info"]["sum"])
                        if 'ндекс' in pm_filter:
                            yandex += int(sale["info"]["sum"])
                        if pm_filter == 'Наличные':
                            cash += int(sale["info"]["sum"])
                        if pm_filter == 'Наличные.':
                            cash_point += int(sale["info"]["sum"])
                        total_cashshifts += int(sale["info"]["sum"])
                    else:
                        send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, '[Admin] Обновите типы оплат')

        total_market = delivery + yandex
        total_cash = total_day - total_cashshifts + cash + cash_point
        total_bn = total_day - total_cash - total_market

        sum_cash_morning = money_record.sum_cash_morning
        sum_cash_end_day = money_record.sum_cash_end_day
        calculated = money_record.calculated
        difference = money_record.difference
        today = True
    else:
        session_number = money_record.session.session_number
        open_date = money_record.session.open_date
        close_date = money_record.session.close_date
        total_day = money_record.total_day
        total_market = money_record.total_market
        total_cash = money_record.total_cash
        total_bn = money_record.total_bn
        cash = money_record.session.cash
        cash_point = money_record.session.cash_point
        yandex = money_record.session.yandex
        delivery = money_record.session.delivery

    return dict(storage=storage, date_at=date_at, today=today, session_number=session_number, open_date=open_date,
                close_date=close_date,
                total_day=total_day, sum_for_percent=total_day - total_market,
                total_cash=total_cash, total_bn=total_bn,
                cash=cash, cash_point=cash_point,
                yandex=yandex, delivery=delivery,
                sum_cash_morning=sum_cash_morning, sum_cash_end_day=sum_cash_end_day,
                calculated=calculated, difference=difference,
                expenses_nal=total_values.get_total_expenses_by_date_and_storage(storage, date_at, False),
                salary_prepayment=total_values.get_total_salary_by_date_and_storage(storage, date_at, 1),
                salary_month=total_values.get_total_salary_by_date_and_storage(storage, date_at, 2),
                payin=total_values.get_total_payin_by_date_and_storage(storage, date_at),
                payout=total_values.get_total_payout_by_date_and_storage(storage, date_at))
