from core.services.api.iiko import IikoService
from apps.iiko.models import Category

from core.validators import validate_field

from typing import List

import json


def update() -> bool:
    json_data = IikoService().get_categories()
    dict_data = json.loads(json_data)
    ids = []

    for i in range(len(dict_data)):
        ids.append(dict_data[i]["id"])
        category = Category.objects.filter(category_id=dict_data[i]["id"]).first()
        if category:
            category.name = dict_data[i]['name']
            category.save()
        else:
            Category.objects.create(
                category_id=dict_data[i]["id"],
                name=dict_data[i]["name"]
            )

    for category in Category.objects.all():
        if category.category_id not in ids:
            category.delete()

    return True


def category_edit(row_id: str | None, is_income: str | None, is_sales: str | None, is_remains: str | None):
    validate_field(row_id, 'идентификатор')

    row = Category.objects.filter(id=row_id).first()

    is_income = True if is_income == 'is_income_1' else False
    is_sales = True if is_sales == 'is_sales_1' else False
    is_remains = True if is_remains == 'is_remains_1' else False

    if row:
        row.is_income = is_income
        row.is_sales = is_sales
        row.is_remains = is_remains
        row.save()
    else:
        raise Category.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')


def categories_all() -> List[Category]:
    return Category.objects.all()


def remain_categories():
    return Category.objects.filter(is_remains=True)
