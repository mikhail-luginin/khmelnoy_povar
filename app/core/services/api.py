from django.conf import settings
from requests import Response

from core.utils import time

from apps.iiko.models import Product, Category

import datetime

import requests

import xml.etree.ElementTree as ET

from core.utils.time import today_date


class IikoService:

    def _iiko_connect(self) -> str:
        url = f'{settings.IIKO_API_URL}/resto/api/auth?login={settings.IIKO_API_LOGIN}&pass={settings.IIKO_API_PASSWORD}'
        response = requests.get(url)
        token = response.text
        return token

    def _iiko_disconnect(self, token: str) -> None:
        url = settings.IIKO_API_URL + '/resto/api/logout?key=' + token
        requests.get(url)

    def _iiko_request(self, url: str, get_params: str = '') -> Response:
        token = self._iiko_connect()

        url = f'{settings.IIKO_API_URL}{url}?key={token}{get_params}'
        response = requests.get(url)

        self._iiko_disconnect(token)

        return response

    def get_nomenclature(self) -> str:
        return self._iiko_request('/resto/api/products', '&includeDeleted=false').text

    def get_payment_types(self) -> str:
        return self._iiko_request('/resto/api/v2/entities/list', '&rootType=PaymentType').text

    def get_suppliers(self):
        return self._iiko_request('/resto/api/suppliers').text

    def get_categories(self):
        return self._iiko_request('/resto/api/v2/entities/products/category/list').text

    def get_cashshifts(self, date_from: str, date_to: str) -> str:
        return self._iiko_request('/resto/api/v2/cashshifts/list',
                                  f'&openDateFrom={date_from}&openDateTo={date_to}&status=ANY').text

    def get_sales_by_department(self, session_id: str) -> str:
        return self._iiko_request(f'/resto/api/v2/cashshifts/payments/list/{session_id}', '&hideAccepted=false').text

    def check_inventory(self, storage_id: str, category_name: str, date_at: str = today_date()) -> str:
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/documents/check/incomingInventory?key=' + token
        category = Category.objects.get(name=category_name)
        items = Product.objects.filter(category=category)
        items_str = '<items>'
        for item in items:
            items_str += f'<item><productId>{item.product_id}</productId><amountContainer>0</amountContainer></item>'
        items_str += '</items>'

        data = f"<?xml version=\"1.0\"?>\r\n<document>\r\n  <documentNumber>{time.get_current_time().strftime('%Y%m%d%H%M%S')}</documentNumber>\r\n  <dateIncoming>{date_at}T23:59:59</dateIncoming>\r\n  <status>NEW</status>\r\n  <storeId>{storage_id}</storeId>\r\n  <comment> </comment>\r\n{items_str}</document>"
        r = requests.post(send_text, data=data, headers={'Content-Type': 'application/xml;charset=UTF-8'})

        self._iiko_disconnect(token)

        return r.text

    def get_storages(self) -> str:
        return self._iiko_request('/resto/api/corporation/stores').text

    def get_storages_groups(self) -> str:
        return self._iiko_request('/resto/api/corporation/groups').text

    def _get_iiko_events(self) -> str:
        return self._iiko_request('/resto/api/events',
                                  f'&from_time={time.get_current_time().strftime("%Y-%m-%d")}T09:00:00.000'
                                  f'&to_time={time.get_current_time() + datetime.timedelta(days=1)}T02:00:00.000').text

    def _get_iiko_events_by_types(self, types: list) -> str:
        token = self._iiko_connect()

        send_text = f'{settings.IIKO_API_URL}/resto/api/events' \
                    f'?from_time={time.get_current_time().strftime("%Y-%m-%d")}T09:00:00.000' \
                    f'&to_time={time.get_current_time() + datetime.timedelta(days=1)}T02:00:00.000&key={token}'

        events = '<eventsRequestData><events>'
        for event_type in types:
            events += f'<event>{event_type}</event>'
        events += '</events></eventsRequestData>'
        r = requests.post(send_text, data=events, headers={'Content-Type': 'application/xml;charset=UTF-8'})

        self._iiko_disconnect(token)

        return r.text

    def get_stop_list_events(self):
        rows = []
        xml = ET.fromstring(self._get_iiko_events())
        for event in xml.findall('event'):
            if event.find('type').text == 'stopListItemAdded' or event.find('type').text == 'stopListItemRemoved':
                dictionary = dict()
                dictionary['date'] = event.find('date').text.split('T')[0] + ' ' + event.find('date').text.split('T')[1]
                dictionary['type'] = event.find('type').text
                for attribute in event.findall('attribute'):
                    name = attribute.find('name').text
                    value = attribute.find('value').text
                    dictionary[name] = value
                rows.append(dictionary)
        return rows

    def get_order_events(self):
        rows = []
        xml = ET.fromstring(self._get_iiko_events_by_types(types=settings.IIKO_ORDER_TYPES))
        for event in xml.findall('event'):
            dictionary = {
                "date": event.find('date').text.split('T')[0] + ' ' + event.find('date').text.split('T')[1],
                "type": event.find('type').text
            }
            for attribute in event.findall('attribute'):
                name = attribute.find('name').text
                value = attribute.find('value').text
                dictionary[name] = value
            rows.append(dictionary)
        
        return rows

    def get_terminals(self) -> str:
        return self._iiko_request('/resto/api/corporation/terminals').text

    def get_discount_types(self) -> str:
        return self._iiko_request('/resto/api/v2/entities/list', '&rootType=DiscountType').text
