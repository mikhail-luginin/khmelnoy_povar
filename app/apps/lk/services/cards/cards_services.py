from django.shortcuts import redirect
from django.contrib import messages

from apps.lk.models import Card

from apps.lk.services.bank import statement_all

from .cards_exceptions import CardUniqueException, CardNotFoundException

from typing import List


class CardService:
    model = Card

    def cards_all(self) -> List[model]:
        return self.model.objects.all()

    def _validate_card(self, num: str, undefined_cards: List[str]) -> bool:
        if num and num not in undefined_cards:
            try:
                self.model.objects.get(num=num)
            except (self.model.DoesNotExist, self.model.MultipleObjectsReturned):
                undefined_cards.append(num)
                return True
        return False

    def _validate_for_unique(self, num: str) -> bool:
        if Card.objects.filter(num=num).exists():
            return True
        return False


    def get_undefined_cards(self) -> List[str]:
        undefined_cards = []

        for statement in statement_all():
            line = statement.payment_purpose.split(' ')

            if 'мерчант' in statement.payment_purpose.lower():
                merchant = line[6][1:13]
                if self._validate_card(merchant, undefined_cards):
                    continue

            if 'отражено' in statement.payment_purpose.lower():
                card_number = line[9][11:]
                if self._validate_card(card_number, undefined_cards):
                    continue

            undefined_cards.append("Undefined card")

        return undefined_cards

    def card_create(self, request) -> redirect:
        name = request.POST.get('name')
        num = request.POST.get('num')
        storage_id = request.POST.get('storage_id')

        if self._validate_card(num, self.get_undefined_cards()):
            raise CardNotFoundException('Карта не найдена')

        if self._validate_for_unique(num):
            raise CardUniqueException('Такая карта уже существует')

        card = self.model.objects.create(
            name=name,
            num=num,
            type=1 if len(num) == 4 else 2,
            storage_id=storage_id)

        for statement in statement_all():
            n = f'**{num}' if len(num) == 4 else num
            if n in statement.payment_purpose and not statement.linked_id:
                statement.linked_id = card.id
                statement.save()
