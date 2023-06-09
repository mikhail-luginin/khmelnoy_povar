#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from typing import List

from apps.lk.models import Expense, ExpenseStatus
from core import validators
from core.services import bar_service


def expenses_all() -> List[Expense]:
    return Expense.objects.all()


def create(date_at: str | None, payment_receiver: str | None,
           expense_sum: float | None, comment: str | None, storage_id: int | None,
           expense_type_id: int | None, expense_source_id: int | None,
           custom_writer: str = False, writer_barmen: bool = False) -> Expense:
    validators.validate_field(date_at, 'дата')
    validators.validate_field(expense_sum, 'сумма расхода')
    validators.validate_field(comment, 'комментарий')
    validators.validate_field(storage_id, 'заведение')
    validators.validate_field(expense_type_id, 'тип расхода')
    validators.validate_field(expense_source_id, 'источник расхода')

    if writer_barmen:
        writer = bar_service.get_main_barmen_on_storage_by_date(date_at=date_at, storage_id=storage_id).employee.fio
    elif custom_writer:
        writer = custom_writer
    else:
        writer = 'Сайт'

    expense = Expense.objects.create(
        date_at=date_at,
        writer=writer,
        payment_receiver=payment_receiver,
        sum=expense_sum,
        comment=comment,
        storage_id=storage_id,
        expense_type_id=expense_type_id,
        expense_source_id=expense_source_id,
    )

    return expense


def edit(expense_id: int | None, date_at: str | None, payment_receiver: str | None,
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

    expense = Expense.objects.filter(id=expense_id).first()
    if expense:
        expense.date_at = date_at
        expense.payment_receiver = payment_receiver
        expense.sum = expense_sum
        expense.comment = comment
        expense.storage_id = storage_id
        expense.expense_type_id = expense_type_id
        expense.expense_source_id = expense_source_id
        expense.save()
    else:
        raise Expense.DoesNotExist('Запись с данным идентификатором не найдена.')


def change_status(expense_id: int, status: str, comment: str) -> ExpenseStatus:
    expense_status = ExpenseStatus.objects.filter(expense_id=expense_id).first()

    match status:
        case 'accept':
            success = True
        case 'deny':
            success = False
        case _:
            return expense_status

    if expense_status:
        expense_status.success = success
        if comment:
            expense_status.comments.append(comment)
        expense_status.save()
    else:
        expense_status = ExpenseStatus.objects.create(expense_id=expense_id, success=success,
                                                      comments=[comment])

    return expense_status
