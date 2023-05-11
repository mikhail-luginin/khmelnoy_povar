from django.shortcuts import redirect

from apps.lk.models import Card

from apps.lk.services.bank import statement_all

from .exceptions import CardUniqueException, CardNotFoundException, CardNameIsNoneException

from typing import List


class CardService:
    model = Card

    def cards_all(self) -> List[model]:
        return self.model.objects.all()

    def _validate_card_exists(self, num: str) -> bool:
        return Card.objects.filter(num=num).exists()

    def _card_not_in_undefined_cards(self, num: str) -> bool:
        if num not in self.get_undefined_cards():
            return False
        return True

    def _validate_card_name(self, name: str) -> bool:
        if name == '':
            return True
        return False
    def get_undefined_cards(self) -> List[str]:
        undefined_cards = []

        for statement in statement_all():
            line = statement.payment_purpose.split(' ')

            if 'мерчант' in statement.payment_purpose.lower():
                merchant = line[6][1:13]
                if not self._validate_card_exists(merchant) and merchant not in undefined_cards:
                    undefined_cards.append(merchant)

            if 'отражено' in statement.payment_purpose.lower():
                card_number = line[9][11:]
                if not self._validate_card_exists(card_number) and card_number not in undefined_cards:
                    undefined_cards.append(card_number)


        return undefined_cards

    def card_create(self, request) -> redirect:
        name = request.POST.get('name')
        num = request.POST.get('num')
        storage_id = request.POST.get('storage_id')

        if self._validate_card_name(name):
            raise CardNameIsNoneException('Название карты не может быть пустым')

        if not self._card_not_in_undefined_cards(num):
            raise CardNotFoundException('Карта не найдена')

        if self._validate_card_exists(num):
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

    def card_update(self, request):
        name = request.POST.get('name')
        storage_id = request.POST.get('storage_id')

        if self._validate_card_name(name):
            raise CardNameIsNoneException('Название карты не может быть пустым')

        Card.objects.filter(id=request.GET.get('id')).update(name=name, storage_id=storage_id)

