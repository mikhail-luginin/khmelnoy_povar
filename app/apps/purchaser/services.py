from core.time import today_date
from core import validators

from apps.lk.models import Expense
from apps.lk.services.catalog import CatalogService


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