from core import validators

from apps.lk.models import Role

def roles_all() -> list[Role]:
    return Role.objects.all()

def create(role_name: str | None, can_all: bool | None, can_create: bool | None,
           can_edit: bool | None, can_delete: bool | None, can_view: list | None) -> None:
    validators.validate_field(role_name, 'наименование роли')

    role = Role.objects.create(name=role_name, can_all=can_all, can_create=can_create, can_edit=can_edit,
                                     can_delete=can_delete)
    role.can_view.set(can_view)
    role.save()

def edit(role_id: int | None, role_name: str | None, can_all: bool | None, can_create: bool | None,
         can_edit: bool | None, can_delete: bool | None, can_view: list | None) -> None:
    validators.validate_field(role_id, 'идентификатор записи')
    validators.validate_field(role_name, 'наименование роли')

    role = Role.objects.filter(id=role_id).first()
    if role:
        role.name = role_name
        role.can_all = can_all
        role.can_create = can_create
        role.can_edit = can_edit
        role.can_delete = can_delete
        role.can_view.set(can_view)
        role.save()
    else:
        raise Role.DoesNotExist('Запись с указанным идентификатором не найдена.')
