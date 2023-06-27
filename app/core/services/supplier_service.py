from apps.iiko.models import Supplier
from core.services.api.iiko import IikoService

from core.validators import validate_field

from typing import List

import xml.etree.ElementTree as ET


def update():
    root = ET.fromstring(IikoService().get_suppliers())
    ids = []

    for country in root.findall('employee'):
        supplier_id = country.find('id').text
        code = country.find('code').text
        name = country.find('name').text

        ids.append(supplier_id)

        obj = Supplier.objects.filter(supplier_id=supplier_id).exists()
        if obj:
            try:
                supplier = Supplier.objects.get(supplier_id=supplier_id)
            except Supplier.DoesNotExist:
                return False
            supplier.name = name
            supplier.save()
        else:
            Supplier.objects.create(
                supplier_id=supplier_id,
                code=code,
                name=name,
                deleted=False,
                friendly_name=name
            )

    for supplier in Supplier.objects.all():
        if supplier.supplier_id not in ids:
            supplier.delete()

    return True

def supplier_edit(row_id: str | None, friendly_name: str | None, category: List | None, is_revise: str | None):
    validate_field(row_id, 'идентификатор')
    validate_field(category, 'категория')

    row = Supplier.objects.filter(id=row_id)

    if row.exists():
        row = row.first()
        row.friendly_name = friendly_name
        row.category.set(category)
        row.is_revise = 0 if not is_revise else int(is_revise)
        row.save()
    else:
        raise Supplier.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')

def suppliers_all() -> List[Supplier]:
    return Supplier.objects.all()
