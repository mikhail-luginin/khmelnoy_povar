from core import validators

from apps.repairer.models import Malfunction
from core.logs import create_log


class MalfunctionService:
    model = Malfunction

    def all(self) -> list[model]:
        return self.model.objects.all()

    def malfunction_create(self, storage_id: int, photo, fault_object: str, description: str) -> None:
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(photo, 'фото')
        validators.validate_field(fault_object, 'объект неисправности')
        validators.validate_field(description, 'описание')

        row = self.model.objects.create(storage_id=storage_id,
                                        photo=photo,
                                        fault_object=fault_object,
                                        description=description)
        create_log(owner=f'CRM {row.storage.name}', entity=row.storage.name, row=row,
                   action='create', additional_data='Неисправность добавлена')

    def malfunctions_get(self, storage_id: int) -> list[model]:
        return self.model.objects.filter(storage_id=storage_id)
