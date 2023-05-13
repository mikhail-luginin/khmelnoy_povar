from django.shortcuts import redirect

from apps.lk.models import Card

from apps.lk.services.bank import statement_all

from .exceptions import CardUniqueException, CardNotFoundException, CardNameIsNoneException, FieldNotFoundError

from typing import List


class CardService:
    model = Card

    def cards_all(self) -> List[model]:
        return self.model.objects.all()

    def get_undefined_cards(self) -> List[str]:
        undefined_cards = []

        for statement in statement_all():
            line = statement.payment_purpose.split(' ')

            if 'мерчант' in statement.payment_purpose.lower():
                merchant = line[6][1:13]
                if not Card.objects.filter(num=merchant).exists() and merchant not in undefined_cards:
                    undefined_cards.append(merchant)

            if 'отражено' in statement.payment_purpose.lower():
                card_number = line[9][11:]
                if not Card.objects.filter(num=card_number).exists() and card_number not in undefined_cards:
                    undefined_cards.append(card_number)


        return undefined_cards

    def card_create(self, name: str | None, num: str | None, storage_id: str | None) -> None:

        if name == '':
            raise CardNameIsNoneException('Название карты не может быть пустым')

        if num not in self.get_undefined_cards():
            raise CardNotFoundException('Карта не найдена')

        if Card.objects.filter(num=num).exists():
            raise CardUniqueException('Такая карта уже существует')

        card = self.model.objects.create(name=name,
                                         num=num,
                                         type=1 if len(num) == 4 else 2,
                                         storage_id=storage_id)

        for statement in statement_all():
            n = f'**{num}' if len(num) == 4 else num
            if n in statement.payment_purpose and not statement.linked_id:
                statement.linked_id = card.id
                statement.save()

    def card_update(self, row_id: str | None, name: str | None, storage_id: str | None):

        if not row_id:
            raise FieldNotFoundError('Идентификатор записи в справочнике не найдены.')

        if not name:
            raise FieldNotFoundError('Наименование в справочнике не найдено.')
        if name == '':
            raise CardNameIsNoneException('Название карты не может быть пустым')

        if not storage_id:
            raise FieldNotFoundError('Заведение в справочнике не найдено.')
        row = self.model.objects.filter(id=row_id)
        if row.exists():
            row = row.first()
            row.name = name
            row.storage_id = storage_id
            row.save()
        else:
            raise self.model.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')
