#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

import json

from django.db.models import Q

from apps.bar.models import Money
from apps.bar.tasks import add_percent_and_premium_to_timetable
from apps.iiko.models import PaymentType, Session
from core import validators
from core.services.api.iiko import IikoService
from core.utils.total_values import get_total_expenses_by_date_and_storage, \
    get_total_payin_by_date_and_storage, get_total_payout_by_date_and_storage, get_total_salary_by_date_and_storage


def update(row_id: int | None) -> None:
    if type(row_id) is str:
        validators.validate_field(row_id, 'идентификатор записи')

    money_record = Money.objects.filter(id=row_id).first()
    if money_record:
        if money_record.sum_cash_end_day and money_record.sum_cash_end_day != 0:
            date_at = money_record.date_at
            storage = money_record.storage

            expenses = get_total_expenses_by_date_and_storage(storage, date_at, False)
            salary_avans = get_total_salary_by_date_and_storage(storage, date_at, 1)
            salary_calculated = get_total_salary_by_date_and_storage(storage, date_at, 2)
            payin = get_total_payin_by_date_and_storage(storage, date_at)
            payout = get_total_payout_by_date_and_storage(storage, date_at)
            point_of_sale = storage.point_of_sale

            total_day = 0
            cash = 0
            cash_point = 0
            delivery = 0
            yandex = 0
            total_cashshifts = 0

            open_date = None
            close_date = None
            session_number = None

            cashshifts_data = json.loads(IikoService().get_cashshifts(str(date_at), str(date_at)))

            for i in range(len(cashshifts_data)):
                if cashshifts_data[i]["pointOfSaleId"] == point_of_sale:
                    first_data = IikoService().get_sales_by_department(cashshifts_data[i]["id"])
                    data = json.loads(first_data)
                    total_day += cashshifts_data[i]["payOrders"]

                    open_date = cashshifts_data[i]["openDate"]
                    if open_date is not None:
                        open_date = f'{open_date.split("T")[0]} {open_date.split("T")[1]}'
                    close_date = cashshifts_data[i]["closeDate"]
                    if close_date is not None:
                        close_date = f'{close_date.split("T")[0]} {close_date.split("T")[1]}'

                    session_number = cashshifts_data[i]["sessionNumber"]

                    for a in range(len(data["cashlessRecords"])):
                        row = PaymentType.objects.get(payment_id=data["cashlessRecords"][a]["info"]["paymentTypeId"])
                        if row.name == 'Наличные':
                            cash += int(data["cashlessRecords"][a]["info"]["sum"])
                        if row.name == 'Наличные.':
                            cash_point += int(data["cashlessRecords"][a]["info"]["sum"])
                        if row.name == 'Delivery Club':
                            delivery += int(data["cashlessRecords"][a]["info"]["sum"])
                        if row.name == 'Яндекс ЕДА' or row.name == '-Яндекс ЕДА':
                            yandex += int(data["cashlessRecords"][a]["info"]["sum"])
                        total_cashshifts += data["cashlessRecords"][a]["info"]["sum"]
            nal = int(total_day) - int(total_cashshifts)
            sum_nal = int(cash) + nal + int(cash_point)
            sum_bn = int(total_day) - sum_nal - int(yandex) - int(delivery)

            calculated = money_record.sum_cash_morning + sum_nal - expenses - salary_calculated - salary_avans - payout + payin

            money_record.total_day = total_day
            money_record.total_cash = sum_nal
            money_record.total_bn = sum_bn
            money_record.total_market = yandex + delivery
            money_record.total_expenses = expenses
            money_record.total_salary = salary_avans + salary_calculated
            money_record.total_payin = payin
            money_record.total_payout = payout
            money_record.calculated = calculated
            money_record.difference = money_record.sum_cash_end_day - calculated

            if money_record.session:
                money_record.session.storage = storage
                money_record.session.date_at = date_at
                money_record.session.session_number = session_number
                money_record.session.open_date = open_date
                money_record.session.close_date = close_date
                money_record.session.cash = cash
                money_record.session.cash_point = cash_point
                money_record.session.yandex = yandex
                money_record.session.delivery = delivery
            else:
                session = Session.objects.create(storage_id=storage.id, date_at=date_at,
                                                 session_number=session_number, open_date=open_date,
                                                 close_date=close_date, cash=cash, cash_point=cash_point,
                                                 yandex=yandex, delivery=delivery)
                money_record.session_id = session.id
            money_record.save()
    else:
        raise Money.DoesNotExist('Запись с указанным идентификатором не найдена.')

    # if calculated > money_record.sum_cash_end_day:
    #     main_barmen = get_main_barmen(date_at, storage.id)
    #     fine = Fine(
    #         date_at=today_date(),
    #         employee=main_barmen,
    #         sum=calculated - money_record.sum_cash_end_day,
    #         reason=Catalog.objects.get(name='Недостача').id,
    #         status=False
    #     )
    #     fine.save()

def get_all() -> list[Money]:
    return Money.objects.all()


def money_edit(row_id: int | None, sum_cash_morning: int | None,
               sum_cash_end_day: int | None, barmen_percent: float | None) -> None:
    validators.validate_field(row_id, 'идентификатор записи')
    validators.validate_field(sum_cash_morning, 'касса утро')
    validators.validate_field(barmen_percent, 'процент бармена')

    money_record = Money.objects.filter(id=row_id).first()
    if money_record:
        money_record.sum_cash_morning = sum_cash_morning
        if sum_cash_end_day:
            money_record.sum_cash_end_day = sum_cash_end_day
        money_record.barmen_percent = barmen_percent
        money_record.save()
        update(row_id=money_record.id)
        if barmen_percent:
            add_percent_and_premium_to_timetable(date_at=money_record.date_at,
                                                 storage_id=money_record.storage_id)
    else:
        raise Money.DoesNotExist('Запись с указанным идентификатором не найдена.')


def rows_with_difference():
    return Money.objects.filter(Q(difference__gt=100) | Q(difference__lt=-100))


def money_get(date_at: str, storage_id: int) -> Money | None:
    return Money.objects.filter(date_at=date_at, storage_id=storage_id).first()


def create_money_record(date_at: str, storage_id: int, sum_cash_morning: int, barmen_percent: float) -> Money:
    return Money.objects.create(date_at=date_at, storage_id=storage_id, sum_cash_morning=sum_cash_morning,
                                barmen_percent=barmen_percent)