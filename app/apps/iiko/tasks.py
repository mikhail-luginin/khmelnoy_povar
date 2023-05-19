from django.conf import settings

from apps.bar.models import TovarRequest
from apps.iiko.services.storage import StorageService
from config.celery import app

from core.telegram import send_message_to_telegram

from apps.iiko.models import Product, StopList
from apps.iiko.services.api import IikoService

import datetime


@app.task
def iiko_stoplist_items():
    for row in IikoService().get_stop_list_events():
        terminal = row.get('terminal')
        storage = None

        for st in StorageService().storages_all():
            if terminal in st.terminal_ids and not storage:
                storage = st

        if storage:
            date_string = row['date'].split('.')[0]
            date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

            product_id = row['productId']

            try:
                product = Product.objects.get(product_id=product_id)
            except Product.DoesNotExist:
                send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS,
                                         f'[CeleryTask: stoplist ({today_datetime()})] '
                                         f'Продукт с идентификатором {product_id} не найден.')
                continue

            if row['type'] == 'stopListItemRemoved':
                try:
                    stoplist_item_for_delete = StopList.objects.get(storage=storage,
                                                                    product=product)
                    stoplist_item_for_delete.delete()
                except StopList.DoesNotExist:
                    continue
                try:
                    tovar_request_for_delete = TovarRequest.objects.filter(storage=storage,
                                                                           product=product,
                                                                           date_at=date.strftime('%Y-%m-%d'))
                    tovar_request_for_delete.delete()
                except TovarRequest.DoesNotExist:
                    continue
            if row['type'] == 'stopListItemAdded':
                stoplist_item = StopList.objects.filter(storage=storage,
                                                        product=product).exists()
                tovar_request = TovarRequest.objects.filter(storage=storage,
                                                            product=product,
                                                            date_at=date.strftime('%Y-%m-%d')).exists()

                if not stoplist_item:
                    StopList.objects.create(date_at=date,
                                            storage=storage,
                                            product=product)

                if not tovar_request:
                    TovarRequest.objects.create(
                        date_at=date.strftime('%Y-%m-%d'),
                        storage=storage,
                        product=product,
                        product_amount=1,
                        product_main_unit='task',
                        supplier=product.supplier
                    )
