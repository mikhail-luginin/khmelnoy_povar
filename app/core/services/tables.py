from django.conf import settings

from core.services.api import IikoService
from core.services.terminal import TerminalService


class OnlineTableService:

    def current_tables(self):
        tables = {}
        for event in IikoService().get_events_by_types(types=settings.IIKO_ORDER_TYPES):
            terminal = TerminalService().terminal_by_uuid(uuid=event.get('terminal'))
            if terminal:
                storage = terminal.storage
            else:
                continue

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

            table["storage_name"] = storage.name
            table["is_open"] = is_open
            table["type"] = event.get('type')

        return tables
