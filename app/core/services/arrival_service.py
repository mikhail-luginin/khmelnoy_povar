#  Copyright (c) 2023. All rights reserved. Mikhail Luginin. Contact: telegram @hex0z

from django.conf import settings
from django.db import transaction
from django.http import QueryDict

from apps.bar.models import Arrival, ArrivalKeg
from core import exceptions
from core.services import product_service, expenses_service, catalog_service
from core.utils.payment_types import get_nal_category, get_bn_category
from core.utils.time import today_date


class ArrivalService:

    def _prepare_invoice_drinks_data(self, data: QueryDict) -> dict:
        arrivals = []

        total_sum = 0
        storage_id = data.get('storage_id')
        invoice_number = data.get('invoice-number')
        payment_type = data.get('payment-type')
        if data.get('kegs'):
            kegs = {
                "gave": {
                    "30": data.get('gave-keg[30]', 0),
                    "50": data.get('gave-keg[50]', 0)
                },
                "received": {
                    "30": data.get('received-keg[30]', 0),
                    "50": data.get('received-keg[50]', 0)
                }
            }
        else:
            kegs = None
        supplier = None

        arrival_type = 2
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
                invoice_row_sum = data.get(f'sum[{invoice_row}]', 0)
                supplier = product.supplier
                arrivals.append(
                    Arrival(date_at=today_date(), storage_id=storage_id, num=invoice_number, product=product,
                            supplier=supplier, amount=amount, sum=invoice_row_sum, type=arrival_type,
                            payment_date=payment_date, payment_type=payment_type)
                )
                total_sum += int(invoice_row_sum)

        return {"arrivals": arrivals, "payment_type": payment_type, "payment_date": payment_date,
                "invoice_number": invoice_number, "total_sum": total_sum, "storage_id": storage_id,
                "supplier": supplier, "kegs": kegs}

    @transaction.atomic()
    def invoice_drinks_create(self, data: QueryDict):
        invoice = self._prepare_invoice_drinks_data(data=data)

        invoice_number = invoice.get('invoice_number')
        payment_date = invoice.get('payment_date')
        payment_type = invoice.get('payment_type')
        storage_id = invoice.get('storage_id')
        supplier = invoice.get('supplier')
        total_sum = invoice.get('total_sum')
        arrivals = invoice.get('arrivals')
        if arrivals:
            Arrival.objects.bulk_create(arrivals)
        if payment_type:
            expense_type_name = settings.TOVAR_ARRIVAL_CATEGORY
            expense_type = catalog_service.get_catalog_by_name(catalog_name=expense_type_name)
            if expense_type:
                expenses_service.create(date_at=payment_date, expense_source_id=payment_type.id, expense_sum=total_sum,
                                        comment=invoice_number, expense_type_id=expense_type.id, storage_id=storage_id,
                                        payment_receiver=supplier if supplier else 'Не указан', writer_barmen=True)
            else:
                raise exceptions.FieldNotFoundError(f'Запись "{expense_type_name}" в справочнике не найдена.')
        kegs = invoice.get('kegs')
        if kegs:
            ArrivalKeg.objects.create(invoice_number=invoice_number,
                                      gave_thirty=kegs['gave']['30'], gave_fifty=kegs['gave']['50'],
                                      received_thirty=kegs['received']['30'], received_fifty=kegs['received']['50'])
