from apps.iiko.models import Product, Category
from core.services import category_service
from core.services.api.iiko import IikoService

from core.validators import validate_field

import xml.etree.ElementTree as ET

from typing import List


def update():
    root = ET.fromstring(IikoService().get_nomenclature())
    ids = []

    for country in root.findall('productDto'):
        product_id = country.find('id').text if country.find('id') is not None else ''
        parent_id = country.find('parentId').text if country.find('parentId') is not None else ''
        num = country.find('num').text if country.find('num') is not None else ''
        code = country.find('code').text if country.find('code') is not None else ''
        name = country.find('name').text if country.find('name') is not None else ''
        product_type = country.find('productType').text if country.find('productType') is not None else ''
        main_unit = country.find('mainUnit').text if country.find('mainUnit') is not None else ''
        product_category = country.find('productCategory').text if country.find(
            'productCategory') is not None else ''

        category_id = None

        if country.find('productGroupType') is None:
            if country.find('productCategory') is not None:
                try:
                    category_id = Category.objects.get(name=product_category)
                except Category.DoesNotExist:
                    category_service.update()
                    category_id = Category.objects.get(name=product_category)

            ids.append(product_id)

            product = Product.objects.filter(product_id=product_id).first()
            if not product:
                Product.objects.create(
                    product_id=product_id,
                    parent_id=parent_id,
                    num=num,
                    code=code,
                    name=name,
                    type=product_type,
                    main_unit=main_unit,
                    category=category_id,
                )
            else:
                product.name = name
                product.type = product_type
                product.main_unit = main_unit
                product.category = category_id
                product.save()

    for product in Product.objects.all():
        if product.product_id not in ids:
            product.delete()

def nomenclature_all() -> List[Product]:
    return Product.objects.all()

def nomenclature_edit(row_id: str | None, minimal: int | None, for_order: int | None,
                      category_id: str | None, supplier_id: str | None):
    validate_field(row_id, 'идентификатор')

    if for_order == '':
        for_order = None

    if minimal == '':
        minimal = None

    row = Product.objects.filter(id=row_id).first()
    if row:
        row.minimal = minimal
        row.for_order = for_order
        row.category_id = category_id
        row.supplier_id = supplier_id
        row.save()
    else:
        raise Product.DoesNotExist(f'Запись в справочнике с идентификатором {row.id} не найдена.')

def product_get(product_id: str = None, row_id: int = None) -> Product | None:
    data = {}

    if product_id:
        data['product_id'] = product_id
    if row_id:
        data['id'] = row_id

    return Product.objects.filter(**data).first()


def nomenclature_by_category(category_name: str) -> Product | None:
    return Product.objects.filter(category__name=category_name)


def nomenclature_by_categories(categories: list):
    return Product.objects.filter(category__name__in=categories)
