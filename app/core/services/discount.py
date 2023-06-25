from core.services.api import IikoService

from apps.iiko.models import DiscountType

import json


class DiscountTypeService:

    def discount_type_by_uuid(self, uuid: str) -> DiscountType | None:
        return DiscountType.objects.filter(uuid=uuid).first()

    def update(self):
        discount_types = IikoService().get_discount_types()
        discount_types = json.loads(discount_types)

        for discount_type in discount_types:
            if not discount_type.get('deleted'):
                DiscountType.objects.create(name=discount_type.get('name'), uuid=discount_type.get('id'))
