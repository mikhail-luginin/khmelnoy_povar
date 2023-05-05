from apps.iiko.models import Product, Category
from apps.iiko.services.category import CategoryService
from apps.iiko.services.api import IikoService

import xml.etree.ElementTree as ET


class ProductService:
    model = Product

    def update(self):
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
                        CategoryService().update()
                        category_id = Category.objects.get(name=product_category)

                ids.append(product_id)

                obj = self.model.objects.filter(product_id=product_id).count()
                if obj == 0:
                    product = self.model(
                        product_id=product_id,
                        parent_id=parent_id,
                        num=num,
                        code=code,
                        name=name,
                        type=product_type,
                        main_unit=main_unit,
                        category=category_id,
                    )
                    product.save()
                else:
                    product = self.model.objects.get(product_id=product_id)
                    product.name = name
                    product.type = product_type
                    product.main_unit = main_unit
                    product.category = category_id
                    product.save()

        for product in self.model.objects.all():
            if product.product_id not in ids:
                product.delete()

        return True
