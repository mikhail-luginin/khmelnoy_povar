from apps.lk.models import Catalog, CatalogType

from typing import List

from core import exceptions


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

    def catalog_type_create(self, name: str | None) -> bool:
        if not name:
            raise exceptions.FieldNotFoundError('Наименование типа справочника не найдено.')
        if name == '':
            raise exceptions.FieldCannotBeEmptyError('Наименование типа справочника не может быть пустым.')
        
        self.catalog_type_model.objects.create(name=name)

        return True

    def catalog_type_edit(self, row_id: int | None, name: str | None) -> bool:
        if not row_id:
            raise exceptions.FieldNotFoundError('Идентификатор записи не найден.')

        if not name:
            raise exceptions.FieldNotFoundError('Наименование записи для типа справочника не найдено.')
        if name == '':
            raise exceptions.FieldCannotBeEmptyError('Наименование записи для типа справочника не может быть пустым.')

        row = self.catalog_type_model.objects.filter(id=row_id)
        if row.exists():
            row = row.first()
            row.name = name
            row.save()
        else:
            raise self.catalog_type_model.DoesNotExist('Записи с данным идентификатором не существует.')

        return True

    def catalog_edit(self, row_id: int | None, name: str | None, linked: list | None) -> bool:
        if not row_id:
            raise exceptions.FieldNotFoundError('Идентификатор записи в справочнике не найден.')

        if not name:
            raise exceptions.FieldNotFoundError('Наименование записи для справочника не найдено.')
        if name == '':
            raise exceptions.FieldCannotBeEmptyError('Наименование записи для справочника не может быть пустым.')

        if not linked:
            raise exceptions.FieldNotFoundError('Типы справочников не найдены.')
        if linked == '':
            raise exceptions.FieldCannotBeEmptyError('Типы справочников не могут быть не заполнены.')

        row = self.catalog_model.objects.filter(id=row_id)
        if row.exists():
            row = row.first()
            row.name = name
            row.catalog_types.set(linked)
            row.save()
            return True
        else:
            raise self.catalog_model.DoesNotExist(f'Запись в справочнике с идентификатором {row_id} не найдена.')

    def catalog_create(self, name: str | None, linked: list | None) -> bool:
        if not name:
            raise exceptions.FieldNotFoundError('Наименование записи для справочника не указано.')
        if name == '':
            raise exceptions.FieldCannotBeEmptyError('Наименование записи для справочника не может быть пустым.')
        
        if not linked:
            raise exceptions.FieldNotFoundError('Поле с типами справочников не найдено.')
        if len(linked) == 0:
            raise exceptions.FieldCannotBeEmptyError('Типы справочников не могут быть не указаны.')

        row = self.catalog_model.objects.create(name=name)
        for link in linked:
            try:
                catalog_type = self.catalog_type_model.objects.get(id=link)
            except self.catalog_type_model.DoesNotExist:
                raise self.catalog_type_model.DoesNotExist(f'Тип справочника с идентификатором {link} не найден.')
            row.catalog_types.add(catalog_type)
        row.save()

        return True
