from typing import List
import json
from django.contrib import messages
from django.shortcuts import redirect
from apps.bar.models import Money
from apps.iiko.models import PaymentType
from apps.iiko.services.api import IikoService
from core.total_values import get_total_expenses_by_date_and_storage, \
    get_total_payin_by_date_and_storage, get_total_payout_by_date_and_storage, get_total_salary_by_date_and_storage


class MoneyService:
    model = Money

    def update(self, request, row_id: int = None) -> redirect:
        record_id = request.GET.get('id') if not row_id else row_id

        if not record_id:
            messages.error(request, 'ID записи не указан.')
            return redirect('/lk/money')

        try:
            money_record = self.model.objects.get(id=record_id)
        except self.model.DoesNotExist:
            messages.error(request, 'Данная запись не найдена')
            return redirect('/lk/money')

        date_at = money_record.date_at
        storage = money_record.storage

        expenses = get_total_expenses_by_date_and_storage(storage, date_at, False)
        salary_avans = get_total_salary_by_date_and_storage(storage, date_at, 1)
        salary_calculated = get_total_salary_by_date_and_storage(storage, date_at, 2)
        payin = get_total_payin_by_date_and_storage(storage, date_at)
        payout = get_total_payout_by_date_and_storage(storage, date_at)
        point_of_sale = storage.point_of_sale

        cashshifts_data = json.loads(IikoService().get_cashshifts(str(date_at), str(date_at)))
        sales_data = (json.loads(IikoService().get_sales_by_department(row["id"])) for row in cashshifts_data
                      if row["pointOfSaleId"] == point_of_sale)
        sales_by_payment = (sale["info"] for sale in sales_data for sale in sale["cashlessRecords"])
        cash_payments = (sale["sum"] for sale in sales_by_payment if
                         PaymentType.objects.get(payment_id=sale["paymentTypeId"]).name in ('Наличные', 'Наличные.'))
        market_payments = (sale["sum"] for sale in sales_by_payment if
                           PaymentType.objects.get(payment_id=sale["paymentTypeId"]).name in (
                           'Delivery Club', 'индекс'))
        total_day = sum(row["payOrders"] for row in cashshifts_data)
        total_cashshifts = sum(sale["sum"] for sale in sales_by_payment)
        unexpected_cash = total_day - total_cashshifts
        total_cash = sum(cash_payments) + unexpected_cash
        total_market = sum(market_payments)
        total_bn = total_day - total_cash - total_market
        calculated = money_record.sum_cash_morning + total_cash - expenses - salary_calculated - salary_avans - payout + payin

        money_record.total_day = total_day
        money_record.total_cash = total_cash
        money_record.total_bn = total_bn
        money_record.total_market = total_market
        money_record.total_expenses = expenses
        money_record.total_salary = salary_avans + salary_calculated
        money_record.total_payin = payin
        money_record.total_payout = payout
        money_record.calculated = calculated
        money_record.difference = calculated - money_record.sum_cash_end_day
        money_record.save()

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

        messages.success(request, 'Запись успешно обновлена')
        return redirect('/lk/money')

    def get_all(self) -> List[model]:
        return self.model.objects.all()

    def money_edit(self, request) -> redirect:
        money_record_id = request.GET.get('id')
        if not money_record_id:
            messages.error(request, 'Не указан идентификатор записи')
            return redirect('/lk/money')

        try:
            money_record = self.model.objects.get(id=money_record_id)
        except self.model.DoesNotExist:
            messages.error(request, 'Запись с данным ID не найдена')
            return redirect('/lk/money')

        sum_cash_morning = request.POST.get('sum_cash_morning')
        sum_cash_end_day = request.POST.get('sum_cash_end_day')
        money_record.sum_cash_morning = sum_cash_morning
        money_record.sum_cash_end_day = sum_cash_end_day
        money_record.save()
        self.update(request, row_id=money_record.id)
        messages.success(request, 'Запись успешно отредактирована')
        return redirect('/lk/money')
