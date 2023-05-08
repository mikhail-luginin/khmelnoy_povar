import json

from apps.bar.models import Timetable, Setting, Money
from apps.iiko.services.api import IikoService
from apps.lk.models import Position, JobPlace, Employee
from apps.iiko.models import Storage, PaymentType

from core import total_values
from core.time import today_date


def get_bar(**kwargs) -> Storage | None:
    try:
        return Storage.objects.get(**kwargs)
    except Storage.DoesNotExist:
        return None


def get_bar_settings() -> Setting:
    return Setting.objects.get(id=1)


def get_position_main_id(is_called: bool, job_name: str) -> int:
    job = JobPlace.objects.get(name=job_name)
    for position in Position.objects.all():
        if position.args['is_usil'] is False and position.args['is_trainee'] is False and position.args['is_called'] is is_called:
            if job in position.linked_jobs.all():
                return position.id


def get_main_barmen(date_at: str, storage: Storage) -> Employee | None:
    if Timetable.objects.filter(date_at=date_at,
                                storage=storage,
                                position_id__in=[
                                    get_position_main_id(False, 'Бармен'),
                                    get_position_main_id(True, 'Бармен')
                                ]).exists() is False:
        return None

    try:
        return Timetable.objects.get(date_at=date_at, storage=storage, position=get_position_main_id(False, 'Бармен')).employee
    except Timetable.DoesNotExist:
        return Timetable.objects.get(date_at=date_at, storage=storage, position=get_position_main_id(True, 'Бармен')).employee


def get_full_information_of_day(date_at: str, storage: Storage) -> dict:
    try:
        money_row = Money.objects.get(date_at=date_at, storage=storage)
    except Money.DoesNotExist:
        return dict(error=True)

    total_day = 0
    cash = 0
    cash_point = 0
    total_cashshifts = 0
    delivery = 0
    yandex = 0

    open_date = None
    close_date = None
    session_number = None

    if date_at == today_date():
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

                # dict = optimize sql queries
                payment_types = dict()
                for payment_type in PaymentType.objects.all():
                    payment_types[payment_type.payment_id] = payment_type.name

                for sale in sales_by_department['cashlessRecords']:
                    pm_filter = payment_types.get(sale["info"]["paymentTypeId"])
                    if 'elivery' in pm_filter:
                        delivery += int(sale["info"]["sum"])
                    if 'ндекс' in pm_filter:
                        yandex += int(sale["info"]["sum"])
                    if pm_filter == 'Наличные':
                        cash += int(sale["info"]["sum"])
                    if pm_filter == 'Наличные.':
                        cash_point += int(sale["info"]["sum"])
                    total_cashshifts += int(sale["info"]["sum"])

        total_market = delivery + yandex
        total_cash = total_day - total_cashshifts + cash + cash_point
        total_bn = total_day - total_cash - total_market
    else:
        total_day = money_row.total_day
        total_bn = money_row.total_bn
        total_market = money_row.total_market
        total_cash = money_row.total_cash

    return dict(session_number=session_number, open_date=open_date, close_date=close_date,
                total_day=total_day, sum_for_percent=total_day - total_market,
                total_cash=total_cash, total_bn=total_bn,
                cash=cash, cash_point=cash_point,
                yandex=yandex, delivery=delivery,
                sum_cash_morning=money_row.sum_cash_morning, sum_cash_end_day=money_row.sum_cash_end_day,
                calculated=money_row.calculated, difference=money_row.difference,
                expenses_nal=total_values.get_total_expenses_by_date_and_storage(storage, date_at, False),
                salary_prepayment=total_values.get_total_salary_by_date_and_storage(storage, date_at, 1),
                salary_month=total_values.get_total_salary_by_date_and_storage(storage, date_at, 2),
                payin=total_values.get_total_payin_by_date_and_storage(storage, date_at),
                payout=total_values.get_total_payout_by_date_and_storage(storage, date_at))
