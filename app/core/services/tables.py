from django.conf import settings

from apps.iiko.models import Storage
from core.services.api import IikoService
from core.services.storage import StorageService


class OnlineTableService:

    def current_tables(self):
        tables = {}
        for event in IikoService().get_events_by_types(types=settings.IIKO_ORDER_TYPES):
            storage_name = None
            for storage in StorageService().storages_all():
                if event.get('terminal') in storage.terminal_ids:
                    storage_name = storage.name

            match event.get('type'):
                case 'orderOpened':
                    is_open = True
                case 'orderPaid' | 'orderPaidNoCash':
                    is_open = False
                case _:
                    continue

            table = tables.get(event.get("orderId"))
            if not table:
                tables[event.get('orderId')] = {}
                table = tables[event.get('orderId')]

            table["storage_name"] = storage_name
            table["is_open"] = is_open
            table["type"] = event.get('type')

        return tables
