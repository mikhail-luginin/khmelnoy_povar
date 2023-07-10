#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from django.conf import settings
from django.db import transaction
from django.http import QueryDict

from apps.bar.models import Arrival, ArrivalKeg, ArrivalInvoice
from config.celery import app
from core import exceptions, validators
from core.services import product_service, expenses_service, catalog_service
from core.utils.payment_types import get_nal_category, get_bn_category
from core.utils.telegram import send_message_to_telegram
from core.utils.time import today_date


class ArrivalService:

    def _prepare_invoice_drinks_data(self, data: QueryDict) -> dict:
        arrivals = []

        total_sum = 0
        storage_id = data.get('storage_id')
        invoice_number = data.get('invoice-number')
        payment_type = data.get('payment-type')
        supplier_id = data.get('supplier_id')
        date_at = data.get('date_at', today_date())
        arrival_type = data.get('arrival_type', 0)

        validators.validate_field(supplier_id, 'Поставщик не может быть не указан.')

        if data.get('kegs'):
            gave_30 = data.get('gave-keg[30]')
            gave_50 = data.get('gave-keg[50]')
            received_30 = data.get('received-keg[30]')
            received_50 = data.get('received-keg[50]')
            kegs = {
                "gave": {
                    "30": gave_30 if gave_30 else 0,
                    "50": gave_50 if gave_50 else 0
                },
                "received": {
                    "30": received_30 if received_30 else 0,
                    "50": received_50 if received_50 else 0
                }
            }
        else:
            kegs = None

        payment_date = today_date()
        match payment_type:
            case 'nal':
                payment_type = get_nal_category()
            case 'bn':
                payment_type = get_bn_category()
            case _:
                payment_type = None
                payment_date = None
                arrival_type = 0

        invoice_rows_count = sum([1 for key in data.keys() if key.startswith('product-id')])
        for invoice_row in range(invoice_rows_count):
            invoice_row = invoice_row + 1
            product_id = data.get(f'product-id[{invoice_row}]')
            product = product_service.product_get(row_id=product_id)
            if product:
                amount = data.get(f'amount[{invoice_row}]')
                invoice_row_sum = data.get(f'sum[{invoice_row}]')
                validators.validate_field(invoice_row_sum, f'Поле "сумма" для {product.name} не может быть пустым.')
                invoice_row_sum = float(invoice_row_sum)

                arrivals.append(
                    Arrival(product=product, amount=amount, sum=invoice_row_sum)
                )
                total_sum += invoice_row_sum

        return {
            "arrivals": arrivals,
            "payment_type": payment_type,
            "payment_date": payment_date,
            "invoice_number": invoice_number,
            "total_sum": total_sum,
            "storage_id": storage_id,
            "supplier_id": supplier_id,
            "kegs": kegs,
            "type": arrival_type,
            "date_at": date_at
        }

    @transaction.atomic()
    def invoice_drinks_create(self, data: QueryDict):
        invoice_data = self._prepare_invoice_drinks_data(data=data)

        date_at = invoice_data.get('date_at')
        invoice_number = invoice_data.get('invoice_number')
        payment_date = invoice_data.get('payment_date')
        payment_type = invoice_data.get('payment_type')
        storage_id = invoice_data.get('storage_id')
        supplier_id = invoice_data.get('supplier_id')
        total_sum = invoice_data.get('total_sum')
        arrivals = invoice_data.get('arrivals')
        arrival_type = invoice_data.get('arrival_type')

        invoice = ArrivalInvoice.objects.create(
            date_at=date_at,
            storage_id=storage_id,
            number=invoice_number,
            supplier_id=supplier_id,
            sum=total_sum,
            payment_date=payment_date,
            payment_type=payment_type,
            type=arrival_type
        )
        if arrivals:
            created_arrivals = Arrival.objects.bulk_create(arrivals)
            for arrival in created_arrivals:
                invoice.arrivals.add(arrival)
            invoice.save()
        if payment_type:
            expense_type_name = settings.TOVAR_ARRIVAL_CATEGORY
            expense_type = catalog_service.get_catalog_by_name(catalog_name=expense_type_name)
            if expense_type:
                expenses_service.create(
                    date_at=payment_date,
                    expense_source_id=payment_type.id,
                    expense_sum=total_sum,
                    comment=invoice_number,
                    expense_type_id=expense_type.id,
                    storage_id=storage_id,
                    payment_receiver=invoice.supplier.name if invoice.supplier else 'Не указан',
                    writer_barmen=True
                )
            else:
                raise exceptions.FieldNotFoundError(f'Запись "{expense_type_name}" в справочнике не найдена.')
        kegs = invoice_data.get('kegs')
        if kegs:
            ArrivalKeg.objects.create(
                invoice_number=invoice_number,
                gave_thirty=kegs['gave']['30'],
                gave_fifty=kegs['gave']['50'],
                received_thirty=kegs['received']['30'],
                received_fifty=kegs['received']['50']
            )


def get_invoices() -> list[dict]:
    arrivals = []
    for arrival in Arrival.objects.all():
        if arrival.num not in [arrvl.get('num') for arrvl in arrivals if arrvl.get('num')]:
            arrivals.append({
                "id": arrival.id,
                "date_at": arrival.date_at,
                "num": arrival.num,
                "supplier_name": arrival.supplier.name if arrival.supplier else 'Не указан'
            })

    return arrivals


def get_arrivals_by_invoice_number(invoice_id: int) -> ArrivalInvoice | None:
    return ArrivalInvoice.objects.filter(id=invoice_id).first()


@app.task
def update_arrivals_to_the_new_version():
    u = 'Что найдено: '
    for arrival in Arrival.objects.all():
        invoice = ArrivalInvoice.objects.filter(
            number=arrival.num,
            storage=arrival.storage,
            date_at=arrival.date_at,
            payment_type=arrival.payment_type,
            payment_date=arrival.payment_date,
            type=arrival.type
        )
        if invoice.count() > 1:
            send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, 'Найден повтор')
            for i in invoice:
                u += f'{i.number} - {i.storage.name} - {i.date_at}\n'

    send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS, u)
    return True
