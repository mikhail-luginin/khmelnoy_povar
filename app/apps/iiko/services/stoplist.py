from typing import List

from apps.iiko.models import Storage, StopList


def stoplist_get() -> List[dict]:
    rows = []

    for storage in Storage.objects.filter(is_office=0):
        row = dict()
        stoplist = []
        row['storage'] = storage.name
        for item in StopList.objects.all():
            if item.storage.id == storage.id:
                stoplist.append(item.product.name)
        row['stoplist'] = stoplist
        rows.append(row)

    return rows
