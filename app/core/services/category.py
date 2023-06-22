from django.shortcuts import redirect

from core.services.api import IikoService
from apps.iiko.models import Category

from core.validators import validate_field

from typing import List

import json


class CategoryService:
    model = Category

    def update(self) -> bool:
        json_data = IikoService().get_categories()
        dict_data = json.loads(json_data)
        ids = []

        for i in range(len(dict_data)):
            ids.append(dict_data[i]["id"])
            obj = self.model.objects.filter(category_id=dict_data[i]["id"]).exists()
            if obj:
                try:
                    category = self.model.objects.get(category_id=dict_data[i]['id'])
                except self.model.DoesNotExist:
                    return False
                category.name = dict_data[i]['name']
                category.save()
            else:

                self.model.objects.create(
                    category_id=dict_data[i]["id"],
                    name=dict_data[i]["name"]
                )

        for category in self.model.objects.all():
            if category.category_id not in ids:
                category.delete()

        return True

    def category_edit(self, row_id: str | None, is_income: str | None, is_sales: str | None, is_remains: str | None) -> redirect:

        validate_field(row_id, 'идентификатор')

        row = self.model.objects.filter(id=row_id)

        is_income = True if is_income == 'is_income_1' else False
        is_sales = True if is_sales == 'is_sales_1' else False
        is_remains = True if is_remains == 'is_remains_1' else False

        if row.exists():
            row = row.first()
            row.is_income = is_income
            row.is_sales = is_sales
            row.is_remains = is_remains
            row.save()
        else:
            raise self.model.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')

    def categories_all(self) -> List[model]:
        return self.model.objects.all()

    def remain_categories(self):
        return self.model.objects.filter(is_remains=True)
