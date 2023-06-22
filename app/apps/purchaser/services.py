from django.conf import settings

from core.time import today_date
from core import validators

from apps.lk.models import Expense
from core.services.catalog import CatalogService

from apps.bar.models import Pays

from .exceptions import DateIsNotEqualCurrentError, RowWasNotCreatedByPurchaser


class PurchaserService:

    def get_rows_by_date(self, date_at: str | None, storage_id: int | None) -> list[Expense]:
        if not date_at:
            date_at = today_date()
        if storage_id:
            return Expense.objects.filter(date_at=date_at, writer='Закупщик', storage_id=storage_id)

        return Expense.objects.filter(date_at=date_at, writer='Закупщик')

    def expense_create(self, date_at: str | None, storage_id: int | None,
                       payment_receiver_id: int | None, expense_source_id: int | None,
                       expense_sum: int | None, comment: str | None) -> None:
        validators.validate_field(date_at, 'дата')
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(payment_receiver_id, 'получатель платежа')
        validators.validate_field(expense_sum, 'сумма')
        validators.validate_field(expense_source_id, 'источник расхода')

        catalog = CatalogService()
        payment_receiver = catalog.get_catalog_by_id(row_id=payment_receiver_id)
        expense_type = catalog.get_catalog_by_name('Продукты')

        Expense.objects.create(
            date_at=date_at,
            writer='Закупщик',
            storage_id=storage_id,
            payment_receiver=payment_receiver.name,
            expense_source_id=expense_source_id,
            expense_type=expense_type,
            sum=expense_sum,
            comment=comment
        )

    def get_money_data(self, date_at: str | None, storage_id: int | None) -> dict[str, int]:
        data = {
            "ip_luginin": 0,
            "ip_moskvichev": 0,
            "ip_luginin_bn": 0,
            "ip_moskvichev_bn": 0,
            "ip_luginin_nal": 0,
            "ip_moskvichev_nal": 0,
            "nal": 0,
            "bn": 0
        }

        filter_params = {
            "date_at": date_at if date_at else today_date(),
            "writer__contains": 'акупщик'
        }
        if storage_id:
            filter_params.update({"storage_id": storage_id})
        for expense in Expense.objects.filter(**filter_params):
            if 'угинин' in expense.storage.entity:
                data['ip_luginin'] += expense.sum
            elif 'осквичев' in expense.storage.entity:
                data['ip_moskvichev'] += expense.sum

            if expense.expense_source.name == settings.PAYMENT_TYPE_BN:
                if 'угинин' in expense.storage.entity:
                    data['ip_luginin_bn'] += expense.sum
                elif 'осквичев' in expense.storage.entity:
                    data['ip_moskvichev_bn'] += expense.sum
                data['bn'] += expense.sum
            elif expense.expense_source.name == settings.PAYMENT_TYPE_NAL:
                if 'угинин' in expense.storage.entity:
                    data['ip_luginin_nal'] += expense.sum
                elif 'осквичев' in expense.storage.entity:
                    data['ip_moskvichev_nal'] += expense.sum
                data['nal'] += expense.sum

        return data

    def delete(self, row_id: int) -> None:
        validators.validate_field(row_id, 'идентификатор записи')

        row = Expense.objects.filter(id=row_id)
        if row.exists():
            row = row.first()
            if str(row.date_at) != today_date():
                raise DateIsNotEqualCurrentError('Запись не была создана сегодня.')
            if row.writer != 'Закупщик':
                raise RowWasNotCreatedByPurchaser('Запись не была создана закупщиком.')
            row.delete()
        else:
            raise Expense.DoesNotExist('Запись с указанным идентификатором не найдена.')

    def get_info_for_purchaser_difference(self):
        rows = []

        for pay in Pays.objects.filter(from_to_id=8):
            row = {
                'date_at': pay.date_at,
                'get': 0,
                'received': 0
            }
            rows.append(row)

        for row in rows:
            for pay in Pays.objects.filter(date_at=row['date_at']):
                row['get'] += pay.sum

            for expense in Expense.objects.filter(date_at=row['date_at'], expense_source_id=3):
                row['received'] += expense.sum

        return rows



