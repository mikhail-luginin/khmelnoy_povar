from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

from apps.lk.models import Statement, Partner, Card
from core import validators

from core.utils.time import today_datetime

import time


class StatementUpdateService:

    def _get_response_from_user(self, request):
        bank_statement = request.FILES.get('file')
        file_system = FileSystemStorage()
        file_name = str('statements/' + today_datetime()) + '.txt'
        saved_file = file_system.save(file_name, bank_statement)

        file_text = open(f'{settings.MEDIA_ROOT}/{saved_file}', 'r', encoding='windows-1251').read()

        return file_text

    def _parse_file(self, file_text) -> list[dict]:
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
            'Плательщик': 'payer',
            'ПлательщикИНН': 'payer_inn',
            'Получатель': 'recipient',
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
                payer = Partner.objects.filter(inn=document['payer_info']['ПлательщикИНН']).first()
                recipient = Partner.objects.filter(inn=document['recipient_info']['ПолучательИНН']).first()

                if not payer:
                    payer_created = Partner(name=document['payer_info']['Плательщик'],
                                            inn=document['payer_info']['ПлательщикИНН'],
                                            friendly_name=document['payer_info']['Плательщик'])
                    payer_created.save()
                    document.pop('payer_info')
                    document['payer_id'] = payer_created.id
                else:
                    document['payer_id'] = payer.id

                if not recipient:
                    recipient_created = Partner(name=document['recipient_info']['Получатель'],
                                                inn=document['recipient_info']['ПолучательИНН'],
                                                friendly_name=document['recipient_info']['Получатель'])
                    recipient_created.save()
                    document.pop('recipient_info')
                    document['recipient_id'] = recipient_created.id
                else:
                    document['recipient_id'] = recipient.id

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
                    linked=linked,
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
        return redirect('/lk/statement')


class PartnerService:
    model = Partner

    def all(self) -> list[model]:
        return self.model.objects.all()

    def edit(self, partner_id: int, friendly_name: str, expense_types: list[int], storages: list[int]) -> None:
        validators.validate_field(partner_id, 'идентификатор записи')
        validators.validate_field(friendly_name, 'имя для отображения')

        partner = self.model.objects.filter(id=partner_id)
        if partner.exists():
            partner = partner.first()
            partner.friendly_name = friendly_name
            partner.storages.set(storages)
            partner.expense_types.set(expense_types)
            partner.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')


class CardService:
    model = Card

    def cards_all(self) -> list[model]:
        return self.model.objects.all()

    def _validate_card(self, num: str) -> bool:
        return self.model.objects.filter(num=num).exists()

    def get_undefined_cards(self) -> list[str]:
        undefined_cards = []

        for statement in Statement.objects.all():
            line = statement.payment_purpose.split(' ')
            num = ''

            if 'мерчант' in statement.payment_purpose.lower():
                num = line[6][1:13]
                if self._validate_card(num):
                    continue

            if 'отражено' in statement.payment_purpose.lower():
                num = line[9][11:]
                if self._validate_card(num):
                    continue

            if num not in undefined_cards:
                undefined_cards.append(num)

        return undefined_cards

    def card_create(self, request) -> redirect:
        name = request.POST.get('name')
        num = request.POST.get('num')
        storage_id = request.POST.get('storage_id')

        card = self.model.objects.create(name=name, num=num, type=1 if len(num) == 4 else 2,
                                         storage_id=storage_id if storage_id != '-1' else None)

        for statement in Statement.objects.all():
            n = f'**{num}' if len(num) == 4 else num
            if n in statement.payment_purpose and not statement.linked:
                statement.linked_id = card.id
                statement.save()

        if self._validate_card(num):
            messages.success(request, 'Карта не найдена.')
        else:
            messages.success(request, 'Карта успешно создана и привязана к уже созданным с ней записям.')
        return redirect('/lk/bank/cards')

    def edit(self, card_id: int, name: str, storage_id: int) -> None:
        validators.validate_field(card_id, 'идентификатор записи')
        validators.validate_field(name, 'наименование')

        card = self.model.objects.filter(id=card_id)
        if card.exists():
            card = card.first()
            card.name = name
            card.storage_id = storage_id
            card.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентфикатором не найдена.')
