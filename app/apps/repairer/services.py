from apps.repairer.models import Malfunction
from core import validators
from core.logs import create_log


class RepairerService:
    model = Malfunction

    def malfunctions_get(self, storage_id: int | None = None) -> list[model]:
        if not storage_id:
            return self.model.objects.all()
        return self.model.objects.filter(storage_id=storage_id)

    def malfunction_repaired(self, malfunction_id: int) -> None:
        validators.validate_field(malfunction_id, 'идентификатор записи')

        malfunction = self.model.objects.filter(id=malfunction_id)
        if malfunction.exists():
            malfunction = malfunction.first()
            malfunction.status = 1
            malfunction.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')

    def malfunction_complete(self, malfunction_id: int, comment: str | None = None) -> None:
        validators.validate_field(malfunction_id, 'идентификатор записи')

        malfunction = self.model.objects.filter(id=malfunction_id)
        if malfunction.exists():
            malfunction = malfunction.first()
            if comment:
                validators.validate_field(comment, 'комментарий')
                malfunction.status = 0
                malfunction.comment = comment
                create_log(owner=f'CRM {malfunction.storage.name}', entity=malfunction.storage.name, row=malfunction,
                           action='edit', additional_data='Неисправность не подтверждена')
            else:
                malfunction.status = 2
                create_log(owner=f'CRM {malfunction.storage.name}', entity=malfunction.storage.name, row=malfunction,
                           action='edit', additional_data='Неисправность подтверждена')
            malfunction.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')
