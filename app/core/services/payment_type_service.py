from core.services.api.iiko import IikoService
from core.validators import validate_field

from apps.iiko.models import PaymentType

import json


def update():
    json_data = IikoService().get_payment_types()
    dict_data = json.loads(json_data)
    ids = []

    for i in range(len(dict_data)):
        ids.append(dict_data[i]["id"])
        obj = PaymentType.objects.filter(payment_id=dict_data[i]["id"]).exists()
        if obj:
            row = PaymentType.objects.get(payment_id=dict_data[i]['id'])
            row.name = dict_data[i]['name']
            row.save()
        else:
            PaymentType.objects.create(
                payment_id=dict_data[i]["id"],
                name=dict_data[i]["name"],
                is_active=0
            )

    for payment_type in PaymentType.objects.all():
        if payment_type.payment_id not in ids:
            payment_type.delete()

    return True


def paymenttype_edit(row_id: str | None, is_active: str | None):
    validate_field(row_id, 'идентификатор')

    row = PaymentType.objects.filter(id=row_id).first()
    if row:
        row.is_active = 0 if not is_active else 1
        row.save()
    else:
        raise PaymentType.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')
