from core.time import get_current_time, monthdelta

from apps.iiko.models import Storage
from apps.lk.models import Fine, Employee

from typing import List


def get_fines_on_storage_by_month(storage: Storage, month_id: str | None) -> List[Fine]:
    current_date = get_current_time()

    if month_id:
        month_id = int(month_id)
        month = monthdelta(current_date, month_id).month
    else:
        month = current_date.month

    return [fine for fine in Fine.objects.filter(employee__storage=storage, date_at__month=month)]
