from core import validators

from apps.bar.models import Pays

from typing import List


def pays_all() -> List[Pays]:
    return Pays.objects.all()

def create(date_at: str | None, storage_id: int | None,
           pay_type: int | None, pay_sum: int | None, comment: str | None,
           from_to_id: int | None = None) -> None:
    validators.validate_field(date_at, 'дата')
    validators.validate_field(storage_id, 'заведение')
    validators.validate_field(pay_sum, 'сумма')
    validators.validate_field(pay_type, 'тип')
    validators.validate_field(comment, 'комментарий')

    Pays.objects.create(
        date_at=date_at,
        storage_id=storage_id,
        type=pay_type,
        from_to_id=from_to_id,
        sum=pay_sum,
        comment=comment
    )

def edit(pay_id: int | None, date_at: str | None, storage_id: int | None,
         pay_type: int | None, pay_sum: int | None, comment: str | None,
         from_to_id: int | None = None) -> None:
    validators.validate_field(pay_id, 'идентификатор записи')
    validators.validate_field(date_at, 'дата')
    validators.validate_field(storage_id, 'заведение')
    validators.validate_field(pay_sum, 'сумма')
    validators.validate_field(pay_type, 'тип')
    validators.validate_field(comment, 'комментарий')

    pay = Pays.objects.filter(id=pay_id).first()
    if pay:
        pay.date_at = date_at
        pay.storage_id = storage_id
        pay.type = pay_type
        pay.sum = pay_sum
        pay.comment = comment
        pay.from_to_id = from_to_id
        pay.save()
    else:
        raise Pays.DoesNotExist('Запись с указанным идентификатором не найдена.')
