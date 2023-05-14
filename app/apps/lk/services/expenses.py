from core import validators

from apps.lk.models import Expense

from typing import List


class ExpenseService:
    model = Expense

    def expenses_all(self) -> List[model]:
        return self.model.objects.all()

    def create(self, date_at: str | None, payment_receiver: str | None,
               expense_sum: float | None, comment: str | None, storage_id: int | None,
               expense_type_id: int | None, expense_source_id: int | None) -> None:
        validators.validate_field(date_at, 'дата')
        validators.validate_field(payment_receiver, 'получатель платежа')
        validators.validate_field(expense_sum, 'сумма расхода')
        validators.validate_field(comment, 'комментарий')
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(expense_type_id, 'тип расхода')
        validators.validate_field(expense_source_id, 'источник расхода')

        self.model.objects.create(
            date_at=date_at,
            writer='Сайт',
            payment_receiver=payment_receiver,
            sum=expense_sum,
            comment=comment,
            storage_id=storage_id,
            expense_type_id=expense_type_id,
            expense_source_id=expense_source_id,
        )

    def edit(self, expense_id: int | None, date_at: str | None, payment_receiver: str | None,
             expense_sum: float | None, comment: str | None, storage_id: int | None,
             expense_type_id: int | None, expense_source_id: int | None) -> None:
        validators.validate_field(expense_id, 'идентификатор записи')
        validators.validate_field(date_at, 'дата')
        validators.validate_field(payment_receiver, 'получатель платежа')
        validators.validate_field(expense_sum, 'сумма расхода')
        validators.validate_field(comment, 'комментарий')
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(expense_type_id, 'тип расхода')
        validators.validate_field(expense_source_id, 'источник расхода')

        expense = self.model.objects.filter(id=expense_id)
        if expense.exists():
            expense = expense.first()
            expense.date_at = date_at
            expense.payment_receiver = payment_receiver
            expense.sum = expense_sum
            expense.comment = comment
            expense.storage_id = storage_id
            expense.expense_type_id = expense_type_id
            expense.expense_source_id = expense_source_id
            expense.save()
        else:
            raise self.model.DoesNotExist('Запись с данным идентификатором не найдена.')
