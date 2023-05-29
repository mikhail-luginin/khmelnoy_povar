from django.contrib import messages
from django.shortcuts import redirect

from apps.bar.tasks import add_percent_and_premium_to_timetable
from core import validators
from core.total_values import get_total_expenses_by_date_and_storage, \
    get_total_payin_by_date_and_storage, get_total_payout_by_date_and_storage, get_total_salary_by_date_and_storage

from apps.bar.models import Money, Timetable
from apps.iiko.models import PaymentType
from apps.iiko.services.api import IikoService

from typing import List

import json


class MoneyService:
    model = Money

    def update(self, row_id: int | None) -> None:
        if type(row_id) is str:
            validators.validate_field(row_id, 'идентификатор записи')

        money_record = self.model.objects.filter(id=row_id)
        if money_record.exists():
            money_record = money_record.first()

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

            cashshifts_data = json.loads(IikoService().get_cashshifts(str(date_at), str(date_at)))

            for i in range(len(cashshifts_data)):
                if cashshifts_data[i]["pointOfSaleId"] == point_of_sale:
                    first_data = IikoService().get_sales_by_department(cashshifts_data[i]["id"])
                    data = json.loads(first_data)
                    total_day += cashshifts_data[i]["payOrders"]

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
            sum_for_percent = total_day - yandex - delivery

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
            money_record.difference = calculated - money_record.sum_cash_end_day
            money_record.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')

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

    def get_all(self) -> List[model]:
        return self.model.objects.all()

    def money_edit(self, row_id: int | None, sum_cash_morning: int | None,
                   sum_cash_end_day: int | None, barmen_percent: float | None) -> None:
        validators.validate_field(row_id, 'идентификатор записи')
        validators.validate_field(sum_cash_morning, 'касса утро')
        validators.validate_field(sum_cash_end_day, 'касса вечер')
        validators.validate_field(barmen_percent, 'процент бармена')

        money_record = self.model.objects.filter(id=row_id)
        if money_record.exists():
            money_record = money_record.first()
            money_record.sum_cash_morning = sum_cash_morning
            money_record.sum_cash_end_day = sum_cash_end_day
            money_record.barmen_percent = barmen_percent
            money_record.save()
            self.update(row_id=money_record.id)
            if barmen_percent:
                add_percent_and_premium_to_timetable.delay(date_at=money_record.date_at,
                                                           storage_id=money_record.storage_id)
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')
