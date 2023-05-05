from apps.iiko.models import PaymentType
from apps.iiko.services.api import IikoService

import json


class PaymentTypeService:
    model = PaymentType

    def update(self):
        json_data = IikoService().get_payment_types()
        dict_data = json.loads(json_data)
        ids = []

        for i in range(len(dict_data)):
            ids.append(dict_data[i]["id"])
            obj = self.model.objects.filter(payment_id=dict_data[i]["id"]).exists()
            if obj:
                row = self.model.objects.get(payment_id=dict_data[i]['id'])
                row.name = dict_data[i]['name']
                row.save()
            else:
                self.model.objects.create(
                    payment_id=dict_data[i]["id"],
                    name=dict_data[i]["name"],
                    is_active=0
                )

        for payment_type in self.model.objects.all():
            if payment_type.payment_id not in ids:
                payment_type.delete()

        return True
