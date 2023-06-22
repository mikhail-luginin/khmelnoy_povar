from apps.bar.models import Setting
from apps.iiko.models import Storage
from core.services.api import IikoService

from typing import List

import uuid
import xml.etree.ElementTree as ET


class StorageService:
    model = Storage

    def update(self):
        storages_xml = ET.fromstring(IikoService().get_storages())
        settings_row = None

        for storage in storages_xml.findall('corporateItemDto'):
            storage_id = storage.find('id').text
            name = storage.find('name').text

            try:
                storage_row = self.model.objects.get(storage_id=storage_id)
            except Storage.DoesNotExist:
                storage_row = self.model(storage_id=storage_id, name=name,
                                         code=uuid.uuid4(), is_office=0, is_hide=0)
                settings_row = Setting(percent=2.5)

            storages_groups_xml = ET.fromstring(IikoService().get_storages_groups())
            for storage_group in storages_groups_xml.findall('groupDto'):
                name_like = storage_group.find('name').text
                if name_like in name:
                    for d in storage_group.findall('pointOfSaleDtoes'):
                        for data in d.findall('pointOfSaleDto'):
                            main = data.find('main').text
                            point_of_sale_id = data.find('id').text

                            if main == 'true':
                                storage_row.point_of_sale = point_of_sale_id
            storage_row.save()

            if settings_row:
                settings_row.storage = storage_row
                settings_row.save()

        return True

    def storages_all(self) -> List[model]:
        return self.model.objects.filter(is_office=0)

    def storage_get(self, **kwargs) -> model | None:
        return self.model.objects.filter(**kwargs).first()
