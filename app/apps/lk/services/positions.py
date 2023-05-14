from django.shortcuts import redirect

from core import validators

from apps.lk.models import Position, JobPlace

from typing import List


class JobsService:
    position_model = Position
    jobs_model = JobPlace

    def positions_all(self) -> List[position_model]:
        return self.position_model.objects.all()

    def position_create(self, position_oklad: int | None, position_is_usil: bool, position_all_storages: bool,
                        position_is_called: bool, position_is_trainee: bool, position_has_percent: bool,
                        position_has_premium: bool, position_name: str | None, priority_id: int | None,
                        position_job_ids: list | None) -> None:
        validators.validate_field(position_oklad, 'оклад')
        validators.validate_field(position_name, 'наименование позиции')
        validators.validate_field(priority_id, 'приоритетный ID')
        validators.validate_field(position_job_ids, 'должности')

        args = {
            "oklad": position_oklad,
            "all_storages": position_all_storages,
            "is_usil": position_is_usil,
            "is_called": position_is_called,
            "is_trainee": position_is_trainee,
            "has_percent": position_has_percent,
            "has_premium": position_has_premium
        }

        row = self.position_model.objects.create(
            name=position_name,
            args=args,
            priority_id=priority_id,
        )

        row.linked_jobs.set(position_job_ids)
        row.save()

    def position_edit(self, position_id: int | None,
                      position_oklad: int | None, position_is_usil: bool, position_all_storages: bool,
                      position_is_called: bool, position_is_trainee: bool, position_has_percent: bool,
                      position_has_premium: bool, position_name: str | None, priority_id: int | None,
                      position_job_ids: list | None) -> redirect:
        validators.validate_field(position_id, 'идентификатор позиции')
        validators.validate_field(position_oklad, 'оклад')
        validators.validate_field(position_name, 'наименование позиции')
        validators.validate_field(priority_id, 'приоритетный ID')
        validators.validate_field(position_job_ids, 'должности')

        row = self.position_model.objects.filter(id=position_id)
        if row.exists():
            row = row.first()
            row.name = position_name
            row.args["oklad"] = position_oklad
            row.args["all_storages"] = position_all_storages
            row.args["is_usil"] = position_is_usil
            row.args["is_called"] = position_is_called
            row.args["is_trainee"] = position_is_trainee
            row.args["has_percent"] = position_has_percent
            row.args["has_premium"] = position_has_premium
            row.priority_id = priority_id
            row.linked_jobs.set(position_job_ids)
            row.save()
        else:
            raise self.position_model.DoesNotExist('Позиция с указанным идентификатором не найдена.')

    def jobs_all(self) -> List[jobs_model]:
        return self.jobs_model.objects.all()

    def job_create(self, job_name: str | None, job_oklad: int | None) -> None:
        validators.validate_field(job_name, 'наименование должности')
        validators.validate_field(job_oklad, 'оклад должности')

        self.jobs_model.objects.create(
            name=job_name,
            oklad=job_oklad
        )

    def job_get(self, **kwargs) -> jobs_model:
        return self.jobs_model.objects.get(**kwargs)
