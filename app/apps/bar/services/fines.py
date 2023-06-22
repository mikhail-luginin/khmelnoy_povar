from core.utils.time import get_current_time, monthdelta

from apps.iiko.models import Storage
from apps.lk.models import Fine

from typing import List


def get_fines_on_storage_by_month(storage: Storage, month: str | None) -> List[Fine]:
    current_date = get_current_time()

    if month:
        month = int(month)
        month = monthdelta(current_date, month).month
    else:
        month = current_date.month

    return [row for row in Fine.objects.filter(date_at__month=month, employee__storage=storage)]
