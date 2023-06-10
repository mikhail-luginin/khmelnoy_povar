from django.conf import settings

from apps.bar.models import TovarRequest
from apps.iiko.services.storage import StorageService
from config.celery import app

from core.telegram import send_message_to_telegram

from apps.iiko.models import Product, StopList
from apps.iiko.services.api import IikoService

import datetime

from core.time import today_datetime


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

            product = Product.objects.filter(product_id=product_id).first()
            if not product:
                send_message_to_telegram(settings.TELEGRAM_CHAT_ID_FOR_ERRORS,
                                         f'[CeleryTask: stoplist ({today_datetime()})] '
                                         f'Продукт с идентификатором {product_id} не найден.')
                continue

            if row['type'] == 'stopListItemRemoved':
                print('removed enter')
                stoplist_item_for_delete = StopList.objects.filter(storage=storage,
                                                                   product=product).first()
                if stoplist_item_for_delete:
                    stoplist_item_for_delete.delete()
                else:
                    continue

                tovar_request_for_delete = TovarRequest.objects.filter(storage=storage,
                                                                       product=product,
                                                                       date_at=date.strftime('%Y-%m-%d')).first()
                if tovar_request_for_delete:
                    tovar_request_for_delete.delete()
                else:
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
                    if 'иво разливное' in product.category.name:
                        TovarRequest.objects.create(
                            date_at=date.strftime('%Y-%m-%d'),
                            storage=storage,
                            product=product,
                            product_amount=1,
                            product_main_unit='task',
                            supplier=product.supplier
                        )
