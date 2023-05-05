from django.shortcuts import redirect

from apps.iiko.services.api import IikoService
from apps.iiko.models import Category

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
                args = dict()

                args['in_remains'] = {'name': 'Остатки', 'status': False}
                args['in_sales'] = {'name': 'Продажи', 'status': False}
                args['in_income'] = {'name': 'Поступления', 'status': False}

                self.model.objects.create(
                    category_id=dict_data[i]["id"],
                    name=dict_data[i]["name"],
                    args=args
                )

        for category in self.model.objects.all():
            if category.category_id not in ids:
                category.delete()

        return True

    def category_edit(self, request, success_url: str) -> redirect:
        category = self.model.objects.get(id=request.GET.get('id'))

        for k, v in category.args.items():
            arg = request.POST.get(k)
            category.args[k]['status'] = True if arg == '1' else False

        category.save()

        return redirect(success_url)

    def categories_all(self) -> List[model]:
        return self.model.objects.all()
