from celery.result import AsyncResult

from typing import List

from apps.iiko.models import Storage, StopList
from apps.iiko.tasks import iiko_stoplist_items


class StoplistService:
    model = StopList

    def update(self):
        task = iiko_stoplist_items.delay()
        result = AsyncResult(task.id)
        status = result.state

        while status != 'SUCCESS':
            result = AsyncResult(task.id)
            status = result.state
            match status:
                case 'SUCCESS':
                    return True
                case 'FAILURE':
                    return False
                case _:
                    continue
        else:
            return True

    def get_stoplist_items(self) -> List[dict]:
        rows = []

        for storage in Storage.objects.filter(is_office=0):
            row = dict()
            stoplist = []
            row['storage_id'] = storage.id
            row['storage'] = storage.district
            for item in StopList.objects.all():
                if item.storage.id == storage.id:
                    stoplist.append(item.product.name)
            row['stoplist'] = stoplist
            rows.append(row)

        return rows
