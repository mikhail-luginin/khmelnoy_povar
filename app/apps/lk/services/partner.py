from django.contrib import messages
from django.shortcuts import redirect

from .cards.exceptions import FieldNotFoundError

from apps.lk.models import Partner

from typing import List


class PartnerService:
    partner_model = Partner

    def get_partners(self) -> List[partner_model]:
        return self.partner_model.objects.all()

    def partner_edit(self, row_id: str | None, friendly_name: str | None, expense_type: list | None, storage_id: list | None):

        if not row_id:
            raise FieldNotFoundError('Идентификатор записи в справочнике не найдены.')

        if not friendly_name:
            raise FieldNotFoundError('Имя для отображения в справочнике не найдено.')

        if not expense_type:
            raise FieldNotFoundError('Типы расхода в справочнике не найдены.')

        if not storage_id:
            raise FieldNotFoundError('Заведения в справочнике не найдены.')

        row = self.partner_model.objects.filter(id=row_id)
        if row.exists():
            row = row.first()
            row.friendly_name = friendly_name
            row.expense_type.set(expense_type)
            row.storage.set(storage_id)
            row.save()
        else:
            raise self.partner_model.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')
