from apps.lk.models import Card

from apps.lk.services.bank import statement_all

from core.exceptions import FieldUniqueError, FieldNotFoundError

from core.validators import validate_field


class CardService:
    model = Card

    def cards_all(self) -> list[model]:
        return self.model.objects.all()

    def get_undefined_cards(self) -> list[str]:
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

        validate_field(name, 'наименование карты')

        if num not in self.get_undefined_cards():
            raise FieldNotFoundError('Карта не найдена')

        if Card.objects.filter(num=num).exists():
            raise FieldUniqueError('Такая карта уже существует')

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

        validate_field(row_id, 'идентификатор')
        validate_field(name, 'наименование карты')
        validate_field(storage_id, 'заведение')

        row = self.model.objects.filter(id=row_id)
        if row.exists():
            row = row.first()
            row.name = name
            row.storage_id = storage_id
            row.save()
        else:
            raise self.model.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')
