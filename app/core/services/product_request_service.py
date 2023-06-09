from django.conf import settings

from core.utils.time import today_date
from core.utils.telegram import send_message_to_telegram

from .api.iiko import IikoService
from . import storage_service
from . import product_service as product_service

import xml.etree.ElementTree as ET

from apps.iiko.models import Storage


class ProductRequestService:

    def _get_remains(self, storage: Storage, category_name: str, date_at: str) -> list[dict]:
        remains = []

        xml = IikoService().check_inventory(storage.storage_id, category_name, date_at)
        items = ET.fromstring(xml)

        for item in items.findall('items/item'):
            name = None
            product_id = None
            supplier_name = 'Не привязан'
            for product in item.findall('product'):
                name = product.find('name').text
                product_id = product.find('id').text
            expected_amount = round(float(item.find('expectedAmount').text))

            product = product_service.product_get(product_id=product_id)
            if product:
                if product.supplier:
                    supplier_name = f'{product.supplier.name} ({product.supplier.friendly_name})'

            remains.append({"id": product_id, "name": name, "amount": expected_amount, "storage_name": storage.name,
                            "supplier_name": supplier_name})

        return remains

    def generate_message(self, date_at: str | None) -> str:
        if not date_at:
            date_at = today_date()

        message = None
        for storage in storage_service.storages_all():
            xml = IikoService().check_inventory(storage.storage_id, 'Бар', date_at=date_at)
            items = ET.fromstring(xml)

            if not message:
                message = f'Дата: {date_at}\nЗаведение: {storage.name}'
            else:
                message += f'\n\nДата: {date_at}\nЗаведение: {storage.name}'

            for item in items.findall('items/item'):
                name = None
                product_id = None
                for product in item.findall('product'):
                    name = product.find('name').text
                    product_id = product.find('id').text
                expected_amount = item.find('expectedAmount').text

                product = product_service.product_get(product_id=product_id)
                if product:
                    if product.minimal:
                        if int(round(float(expected_amount))) <= product.minimal:
                            message += f'\n{name}: {product.for_order}'
                    else:
                        message += f'\n{name}: не указано минимальное значение'
                else:
                    send_message_to_telegram(chat_id=settings.TELEGRAM_CHAT_ID_FOR_ERRORS,
                                             message=f'<b>[ProductRequest]</b> '
                                                     f'Продукт с идентификатором {product_id} не найден.')
        return message

    def remain_products(self, category: str, date_at: str = today_date()) -> list[dict]:
        arr = []
        for storage in storage_service.storages_all():
            arr += self._get_remains(
                storage=storage, category_name=category,
                date_at=date_at
            )

        return arr
