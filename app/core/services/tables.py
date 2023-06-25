import datetime

from core.services.api import IikoService
from core.services.discount import DiscountTypeService
from core.services.terminal import TerminalService


class OnlineTableService:

    def table_by_order_num(self, order_num: str):
        # table = {
        #     "storage_name": None,
        #     "storage_id": None,
        #     "is_open": True,
        #     "is_precheque": False,
        #     "is_deleted": False,
        #     "is_moved": False,
        #     "is_discounted": False,
        #     "time": {
        #         "open": None, "precheque": None, "delete": None, "close": None, "move": None
        #     },
        #     "sum": {
        #         "total": None, "subtotal": None
        #     },
        #     "order_num": None,
        #     "table_num": None,
        #     "num_guests": None,
        #     "discount": {"type": None, "percent": None},
        #     "dishes": None,
        #     "type": None
        # }
        #
        for order_id, table in self.current_tables().items():
            if table['order_num'] == order_num:
                return table

    def current_tables(self):
        tables = {}
        for event in IikoService().get_order_events():
            terminal = TerminalService().terminal_by_uuid(uuid=event.get('terminal'))
            if terminal:
                storage = terminal.storage
            else:
                continue

            is_open = True
            is_precheque = False
            is_deleted = False
            is_discounted = False
            is_moved = False

            date = event.get('date')
            subtotal = event.get('sum')
            total = event.get('orderSumAfterDiscount')
            order_num = event.get('orderNum')
            table_num = event.get('tableNum')
            num_guests = event.get('numGuests')
            discount_type = DiscountTypeService().discount_type_by_uuid(uuid=event.get('discountTypeId'))
            discount_percent = event.get('percent')

            open_time = datetime.datetime.strptime(event.get('openTime'), '%Y-%m-%dT%H:%M:%S.%f')
            precheque_time = event.get('prechequeTime')
            close_time = None
            deleted_time = None
            move_time = None

            dishes = []

            match event.get('type'):
                case 'orderPaid' | 'orderPaidNoCash':
                    is_open = False
                    close_time = date
                    precheque_time = datetime.datetime.strptime(precheque_time, '%Y-%m-%dT%H:%M:%S.%f')
                case 'orderPrechequed':
                    is_precheque = True
                    precheque_time = datetime.datetime.strptime(precheque_time, '%Y-%m-%dT%H:%M:%S.%f')
                case 'orderCancelPrechequed':
                    is_precheque = False
                case 'orderPrepaid':
                    pass
                case 'orderReturned':
                    pass
                case 'orderDeleted':
                    is_deleted = True
                case 'orderMoved':
                    is_moved = True
                case 'orderDiscounted':
                    is_discounted = True
                case 'addItemToOrder':
                    dishes.append({"dish": event.get('dishes'), "count": event.get('rowCount')})
                case 'deletedPrintedItems':
                    for dish in dishes:
                        if dish.get('dish') == event.get('dishes'):
                            dish['is_deleted'] = True
                            dish['comment'] = event.get('comment')
                            dish['reason'] = event.get('reason')
                case _:
                    continue

            table = tables.get(event.get("orderId"))
            if not table:
                tables[event.get('orderId')] = {}
                table = tables[event.get('orderId')]

            table["storage_name"] = storage.name
            table["storage_id"] = storage.id
            table["is_open"] = is_open
            table["is_precheque"] = is_precheque
            table["is_deleted"] = is_deleted
            table["is_moved"] = is_moved
            table["is_discounted"] = is_discounted
            table["time"] = {"open": open_time, "precheque": precheque_time, "delete": deleted_time,
                             "close": close_time, "move": move_time}
            table["sum"] = {"total": total.split('.')[0] if total else 0,
                            "subtotal": subtotal.split('.')[0] if subtotal else 0}
            table["order_num"] = order_num.split('.')[0] if order_num else None
            table["table_num"] = table_num.split('.')[0] if table_num else None
            table["num_guests"] = num_guests.split('.')[0] if num_guests else None
            table["discount"] = {"type": discount_type, "percent": discount_percent}
            table["dishes"] = dishes
            table["type"] = event.get('type')

        return tables
