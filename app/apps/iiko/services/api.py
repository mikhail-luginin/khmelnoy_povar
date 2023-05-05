from django.conf import settings

from core import time

from apps.iiko.models import Product, Category

import datetime

import requests

import xml.etree.ElementTree as ET

from core.telegram import send_message_to_telegram


class IikoService:

    def _iiko_connect(self) -> str:
        url = settings.IIKO_API_URL + '/resto/api/auth?login=' + settings.IIKO_API_LOGIN + '&pass=' + settings.IIKO_API_PASSWORD
        response = requests.get(url)
        return response.text

    def _iiko_disconnect(self, token: str):
        url = settings.IIKO_API_URL + '/resto/api/auth?key=' + token
        requests.get(url)

    def get_nomenclature(self):
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/products?includeDeleted=false&key=' + token
        r = requests.get(send_text)

        self._iiko_disconnect(token)

        return r.text

    def get_payment_types(self):
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/v2/entities/list?rootType=PaymentType&key=' + token
        r = requests.get(send_text)

        self._iiko_disconnect(token)

        return r.text

    def get_suppliers(self):
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/suppliers?key=' + token
        r = requests.get(send_text)

        self._iiko_disconnect(token)

        return r.text

    def get_categories(self):
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/v2/entities/products/category/list?key=' + token
        r = requests.get(send_text)

        self._iiko_disconnect(token)

        return r.text

    def get_cashshifts(self, date_from: str, date_to: str) -> str:
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/v2/cashshifts/list?openDateFrom=' + date_from + '&openDateTo=' + date_to + '&status=ANY&key=' + token
        r = requests.get(send_text)

        self._iiko_disconnect(token)

        return r.text

    def get_sales_by_department(self, session_id: str) -> str:
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/v2/cashshifts/payments/list/' + session_id + '?key=' + token + '&hideAccepted=false'
        r = requests.get(send_text)

        self._iiko_disconnect(token)

        return r.text

    def check_inventory(self, storage_id: str, category_name: str) -> str:
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/documents/check/incomingInventory?key=' + token
        year = time.get_current_time().strftime('%Y')
        month = time.get_current_time().strftime('%m')
        day = time.get_current_time().strftime('%d')
        category = Category.objects.get(name=category_name)
        items = Product.objects.filter(category=category)
        items_str = '<items>'
        for item in items:
            items_str += f'<item><productId>{item.product_id}</productId><amountContainer>0</amountContainer></item>'
        items_str += '</items>'

        data = f"<?xml version=\"1.0\"?>\r\n<document>\r\n  <documentNumber>{time.get_current_time().strftime('%Y%m%d%H%M%S')}</documentNumber>\r\n  <dateIncoming>{datetime.date(int(year), int(month), int(day)) - datetime.timedelta(days=0)}T23:59:59</dateIncoming>\r\n  <status>NEW</status>\r\n  <storeId>{storage_id}</storeId>\r\n  <comment> </comment>\r\n{items_str}</document>"
        r = requests.post(send_text, data=data, headers={'Content-Type': 'application/xml;charset=UTF-8'})

        self._iiko_disconnect(token)

        return r.text

    def get_storages(self) -> str:
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/corporation/stores?key=' + token
        r = requests.get(send_text)
        self._iiko_disconnect(token)
        return r.text

    def get_storages_groups(self) -> str:
        token = self._iiko_connect()

        send_text = settings.IIKO_API_URL + '/resto/api/corporation/groups?key=' + token
        r = requests.get(send_text)
        self._iiko_disconnect(token)
        return r.text

    def get_iiko_events(self, from_time: str, to_time: str):
        token = self._iiko_connect()
        send_text = settings.IIKO_API_URL + '/resto/api/events?key=' + token + '&from_time=' + time.get_current_time().strftime(
            '%Y-%m-%d') + 'T' + from_time + '.000&to_time=' + (time.get_current_time() + datetime.timedelta(days=1)).strftime('%Y-%m-%d') + 'T' + to_time + '.000'
        r = requests.get(send_text)
        self._iiko_disconnect(token)
        return r.text

    def get_stop_list_events(self):
        rows = []
        xml = ET.fromstring(self.get_iiko_events('11:00:00', '01:00:00'))
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
