from django.contrib import messages
from django.shortcuts import redirect

from apps.lk.models import Catalog, CatalogType

from typing import List


class CatalogService:
    catalog_type_model = CatalogType
    catalog_model = Catalog

    def get_catalog_by_type(self, type_name: str) -> List[catalog_type_model]:
        try:
            catalog_type = self.catalog_type_model.objects.get(name=type_name)
            return list(catalog_type.catalog_set.all())
        except self.catalog_type_model.DoesNotExist:
            return []

    def get_catalog_linked_types(self, catalog_id: str) -> List[catalog_type_model]:
        try:
            catalog = self.catalog_model.objects.get(id=catalog_id)
            return catalog.catalog_types.all()
        except self.catalog_model.DoesNotExist:
            return []

    def get_catalog_by_id(self, row_id) -> catalog_model:
        return self.catalog_model.objects.get(id=row_id)

    def get_catalog_by_catalog_type_name_contains(self, name: str) -> List[catalog_model]:
        return self.catalog_model.objects.filter(catalog_types__name__icontains=name)

    def get_catalog_by_catalog_type_name_in_list(self, names: List[str]) -> List[catalog_model]:
        return self.catalog_model.objects.filter(catalog_types__name__in=names)

    def get_catalog_by_name(self, catalog_name: str) -> catalog_model:
        return self.catalog_model.objects.get(name__iexact=catalog_name)

    def get_catalog_types(self) -> List[catalog_type_model]:
        return self.catalog_type_model.objects.all()

    def get_catalog(self) -> List[catalog_model]:
        return self.catalog_model.objects.all()

    def catalog_edit(self, request) -> redirect:
        row_id = request.GET.get('id')
        name = request.POST.get('name')
        linked = request.POST.getlist('linked')

        try:
            row = self.catalog_model.objects.get(id=row_id)
        except Catalog.DoesNotExist:
            messages.error(request, 'Запись не найдена :(')
            return redirect('/lk/catalog')

        row.name = name

        row.catalog_types.set(linked)

        row.save()

        messages.success(request, 'Каталог успешно отредактирован :)')
        return redirect('/lk/catalog')

    def catalog_create(self, request) -> redirect:
        name = request.POST.get('catalog-name')
        linked = request.POST.getlist('linked')

        row = self.catalog_model.objects.create(name=name)

        for link in linked:
            try:
                catalog_type = self.catalog_type_model.objects.get(id=link)
            except self.catalog_type_model.DoesNotExist:
                messages.error(request, f'Объект с идентификатором {link} не найден :(')
                return redirect('/lk/catalog')
            row.catalog_types.add(catalog_type)

        row.save()

        messages.success(request, 'Объект успешно записан в справочник :)')
        return redirect('/lk/catalog')
