from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.contrib import messages

from apps.lk.models import Statement, Partner, Card

from core.time import today_datetime

from typing import List

import time


class StatementUpdateService:

    def _get_response_from_user(self, request):
        bank_statement = request.FILES.get('file')
        file_system = FileSystemStorage()
        file_name = str('statements/' + today_datetime()) + '.txt'
        saved_file = file_system.save(file_name, bank_statement)

        file_text = open('media/' + saved_file, 'r', encoding='windows-1251').read()

        return file_text

    def _parse_file(self, file_text) -> List[dict]:
        exceptions = [
            'ВидПлатежа',
            'ВидОплаты',
            'Код',
            'СтатусСоставителя',
            'ПоказательКБК',
            'ОКАТО',
            'ПоказательОснования',
            'ПоказательПериода',
            'ПоказательНомера',
            'ПоказательДаты',
            'ПоказательТипа',
            'Очередность',
            'ПлательщикКПП',
            'ПлательщикРасчСчет',
            'ПлательщикБанк1',
            'ПлательщикБИК',
            'ПлательщикКорсчет',
            'ПолучательКПП',
            'ПолучательРасчСчет',
            'ПолучательБанк1',
            'ПолучательБИК',
            'ПолучательКорсчет',
            'ПолучательСчет',
            'ПлательщикСчет'
        ]

        translators = {
            'СекцияДокумент': 'document_type',
            'Номер': 'document_number',
            'Дата': 'date',
            'ДатаСписано': 'date_write_off',
            'ДатаПоступило': 'date_receipt',
            'Сумма': 'sum',
            'НазначениеПлатежа': 'payment_purpose',
            'Плательщик': 'payer_id',
            'ПлательщикИНН': 'payer_inn',
            'Получатель': 'recipient_id',
            'ПолучательИНН': 'recipient_inn'
        }

        documents = []
        current_document = dict()
        payer_info = dict()
        recipient_info = dict()

        for line in file_text.splitlines()[1:]:
            if line.startswith('КонецДокумента'):
                documents.append(current_document)
                current_document = dict()
                payer_info = dict()
                recipient_info = dict()
                continue
            if line.startswith('КонецФайла'):
                break

            current_line = line.split('=', maxsplit=1)
            if len(current_line) == 2:
                if current_line[0] not in exceptions:
                    if 'лательщик' in current_line[0]:
                        payer_info[current_line[0]] = current_line[1]
                    elif 'олучатель' in current_line[0]:
                        recipient_info[current_line[0]] = current_line[1]
                    else:
                        current_document[translators.get(current_line[0], None)] = current_line[1]
                        current_document['recipient_info'] = recipient_info
                        current_document['payer_info'] = payer_info
            else:
                continue

        return documents

    def _parse_documents(self, request):
        documents = self._parse_file(self._get_response_from_user(request))

        for document in documents:
            linked = None
            if Statement.objects.filter(document_number=document['document_number']).count() == 0:
                try:
                    payer = Partner.objects.get(inn=document['payer_info']['ПлательщикИНН'])
                except Partner.DoesNotExist:
                    payer = None

                try:
                    recipient = Partner.objects.get(inn=document['recipient_info']['ПолучательИНН'])
                except Partner.DoesNotExist:
                    recipient = None

                if payer is None:
                    payer_created = Partner(name=document['payer_info']['Плательщик'],
                                            inn=document['payer_info']['ПлательщикИНН'],
                                            friendly_name=document['payer_info']['Плательщик'])
                    payer_created.save()
                    document.pop('payer_info')
                    document['payer_id'] = str(payer_created.id)
                else:
                    document['payer_id'] = str(payer.id)

                if recipient is None:
                    recipient_created = Partner(name=document['recipient_info']['Получатель'],
                                                inn=document['recipient_info']['ПолучательИНН'],
                                                friendly_name=document['recipient_info']['Получатель'])
                    recipient_created.save()
                    document.pop('recipient_info')
                    document['recipient_id'] = str(recipient_created.id)
                else:
                    document['recipient_id'] = str(recipient.id)

                document['date'] = time.strftime('%Y-%m-%d', time.strptime(document['date'], '%d.%m.%Y')) if document[
                                                                                                                 'date'] != '' else None
                document['date_write_off'] = time.strftime('%Y-%m-%d',
                                                           time.strptime(document['date_write_off'], '%d.%m.%Y')) if \
                    document['date_write_off'] != '' else None
                document['date_receipt'] = time.strftime('%Y-%m-%d',
                                                         time.strptime(document['date_receipt'], '%d.%m.%Y')) if \
                    document['date_receipt'] != '' else None

                for card in Card.objects.all():
                    if card.num in document['payment_purpose']:
                        linked = card.id

                data = dict(
                    linked_id=linked,
                    document_type=document['document_type'],
                    document_number=document['document_number'],
                    date=document['date'],
                    date_write_off=document['date_write_off'],
                    date_receipt=document['date_receipt'],
                    sum=document['sum'],
                    payer_id=document['payer_id'],
                    recipient_id=document['recipient_id'],
                    payment_purpose=document['payment_purpose'],
                )
                self._create_statement(data)

    def _create_statement(self, data: dict) -> None:
        Statement.objects.create(**data)

    def update(self, request):
        self._parse_documents(request)
        messages.success(request, 'Выписка успешно загружена :)')
        return redirect('/lk/bank')


def statement_all() -> List[Statement]:
    return Statement.objects.all()


def partners_all() -> List[Partner]:
    return Partner.objects.all()


class CardService:
    model = Card

    def cards_all(self) -> List[model]:
        return self.model.objects.all()

    def validate_card(self, num: str, undefined_cards: List[str]) -> bool:
        if num and num not in undefined_cards:
            try:
                self.model.objects.get(num=num)
            except self.model.DoesNotExist:
                undefined_cards.append(num)
                return True
        return False

    def get_undefined_cards(self) -> List[str]:
        undefined_cards = []

        for statement in statement_all():
            line = statement.payment_purpose.split(' ')

            if 'мерчант' in statement.payment_purpose.lower():
                merchant = line[6][1:13]
                if self.validate_card(merchant, undefined_cards):
                    continue

            if 'отражено' in statement.payment_purpose.lower():
                card_number = line[9][11:]
                if self.validate_card(card_number, undefined_cards):
                    continue

            undefined_cards.append("Undefined card")

        return undefined_cards

    def card_create(self, request) -> redirect:
        name = request.POST.get('name')
        num = request.POST.get('num')
        storage_id = request.POST.get('storage_id')
        undefined_cards = []

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

        if self.validate_card(num, undefined_cards):
            messages.success(request, 'Карта не найдена.')
        else:
            messages.success(request, 'Карта успешно создана и привязана к уже созданным с ней записям.')
        return redirect('/lk/bank/cards')
