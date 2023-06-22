from core import validators

from apps.lk.models import Role


class RoleService:
    model = Role

    def roles_all(self) -> list[model]:
        return self.model.objects.all()

    def create(self, role_name: str | None, can_all: bool | None, can_create: bool | None,
               can_edit: bool | None, can_delete: bool | None, can_view: list | None) -> None:
        validators.validate_field(role_name, 'наименование роли')

        role = self.model.objects.create(name=role_name, can_all=can_all, can_create=can_create, can_edit=can_edit,
                                         can_delete=can_delete)
        role.can_view.set(can_view)
        role.save()

    def edit(self, role_id: int | None, role_name: str | None, can_all: bool | None, can_create: bool | None,
             can_edit: bool | None, can_delete: bool | None, can_view: list | None) -> None:
        validators.validate_field(role_id, 'идентификатор записи')
        validators.validate_field(role_name, 'наименование роли')

        role = self.model.objects.filter(id=role_id)
        if role.exists():
            role = role.first()
            role.name = role_name
            role.can_all = can_all
            role.can_create = can_create
            role.can_edit = can_edit
            role.can_delete = can_delete
            role.can_view.set(can_view)
            role.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')
