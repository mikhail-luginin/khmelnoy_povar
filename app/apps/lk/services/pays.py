from core import validators

from apps.bar.models import Pays

from typing import List


class PaysService:
    model = Pays

    def pays_all(self) -> List[model]:
        return self.model.objects.all()

    def create(self, date_at: str | None, storage_id: int | None,
               pay_type: int | None, pay_sum: int | None, comment: str | None) -> None:
        validators.validate_field(date_at, 'дата')
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(pay_sum, 'сумма')
        validators.validate_field(pay_type, 'тип')
        validators.validate_field(comment, 'комментарий')

        self.model.objects.create(
            date_at=date_at,
            storage_id=storage_id,
            type=pay_type,
            sum=pay_sum,
            comment=comment
        )

    def edit(self, pay_id: int | None, date_at: str | None, storage_id: int | None,
             pay_type: int | None, pay_sum: int | None, comment: str | None) -> None:
        validators.validate_field(pay_id, 'идентификатор записи')
        validators.validate_field(date_at, 'дата')
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(pay_sum, 'сумма')
        validators.validate_field(pay_type, 'тип')
        validators.validate_field(comment, 'комментарий')

        pay = self.model.objects.filter(id=pay_id)
        if pay.exists():
            pay = pay.first()
            pay.date_at = date_at
            pay.storage_id = storage_id
            pay.type = pay_type
            pay.sum = pay_sum
            pay.comment = comment
            pay.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')
