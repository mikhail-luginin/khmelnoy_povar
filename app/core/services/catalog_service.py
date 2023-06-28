from apps.lk.models import Catalog, CatalogType

from typing import List

from core import validators


def get_catalog_by_type(type_name: str) -> List[CatalogType]:
    catalog_type = CatalogType.objects.filter(name=type_name).first()
    if catalog_type:
        return list(catalog_type.catalog_set.all())
    else:
        return []


def get_catalog_linked_types(catalog_id: str) -> List[CatalogType]:
    catalog = Catalog.objects.filter(id=catalog_id).first()
    if catalog:
        return catalog.catalog_types.all()
    else:
        return []


def get_catalog_by_id(row_id) -> Catalog:
    return Catalog.objects.filter(id=row_id).first()


def get_catalog_by_catalog_type_name_contains(name: str) -> list[Catalog]:
    return Catalog.objects.filter(catalog_types__name__icontains=name)


def get_catalog_by_catalog_type_name_in_list(names: List[str]) -> list[Catalog]:
    return Catalog.objects.filter(catalog_types__name__in=names)


def get_catalog_by_name(catalog_name: str) -> Catalog:
    return Catalog.objects.filter(name__icontains=catalog_name).first()


def get_catalog_types() -> list[CatalogType]:
    return CatalogType.objects.all()


def get_catalog() -> list[Catalog]:
    return Catalog.objects.all()


def catalog_type_create(name: str):
    validators.validate_field(name, 'наименование')
    
    CatalogType.objects.create(name=name)


def catalog_type_edit(row_id: int, name: str):
    validators.validate_field(row_id, 'идентификатор записи')
    validators.validate_field(name, 'наименование')

    row = CatalogType.objects.filter(id=row_id).first()
    if row:
        row.name = name
        row.save()
    else:
        raise CatalogType.DoesNotExist('Записи с данным идентификатором не существует.')


def catalog_edit(row_id: int, name: str, linked: list):
    validators.validate_field(row_id, 'идентификатор записи')
    validators.validate_field(name, 'наименование')
    validators.validate_field(linked, 'типы справочника')

    row = Catalog.objects.filter(id=row_id).first()
    if row:
        row.name = name
        row.catalog_types.set(linked)
        row.save()
    else:
        raise Catalog.DoesNotExist(f'Запись в справочнике с идентификатором {row_id} не найдена.')


def catalog_create(name: str, linked: list):
    validators.validate_field(name, 'наименование')
    validators.validate_field(linked, 'типы справочника')

    row = Catalog.objects.create(name=name)
    for link in linked:
        try:
            catalog_type = CatalogType.objects.get(id=link)
        except CatalogType.DoesNotExist:
            raise CatalogType.DoesNotExist(f'Тип справочника с идентификатором {link} не найден.')
        row.catalog_types.add(catalog_type)
    row.save()

    return row
