from django.shortcuts import redirect
from django.contrib import messages

from apps.lk.models import Position, JobPlace

from typing import List

from core import exceptions


class JobsService:
    position_model = Position
    jobs_model = JobPlace

    def positions_all(self) -> List[position_model]:
        return self.position_model.objects.all()

    def position_create(self, position_oklad: str | None,
                        position_is_usil: bool,
                        position_all_storages: bool,
                        position_is_called: bool,
                        position_is_trainee: bool,
                        position_has_percent: bool,
                        position_has_premium: bool,
                        position_name: str | None,
                        priority_id: str | None,
                        position_job_ids: list | None) -> bool:
        if not position_oklad:
            raise exceptions.FieldNotFoundError('Поле с окладом позиции не найдено.')
        if position_oklad == '':
            raise exceptions.FieldCannotBeEmptyError('Поле с окладом позиции не может быть пустым.')

        if not position_name:
            raise exceptions.FieldNotFoundError('Поле с наименованием позиции не найдено.')
        if position_name == '':
            raise exceptions.FieldCannotBeEmptyError('Поле с наименованием позиции не может быть пустым.')

        if not priority_id:
            raise exceptions.FieldNotFoundError('Поле с приоритетным ID позиции не найдено.')
        if priority_id == '':
            raise exceptions.FieldCannotBeEmptyError('Поле с приоритетным ID позиции не может быть пустым.')

        if not position_job_ids:
            raise exceptions.FieldNotFoundError('Поле с, привязанными к позиции, должностями не найдено.')
        if position_job_ids == '':
            raise exceptions.FieldCannotBeEmptyError('Поле с, привязанными к позиции, должностями не может быть пустым.')

        args = dict()
        args['oklad'] = position_oklad
        args['all_storages'] = position_all_storages
        args['is_usil'] = position_is_usil
        args['is_called'] = position_is_called
        args['is_trainee'] = position_is_trainee
        args['has_percent'] = position_has_percent
        args['has_premium'] = position_has_premium

        row = self.position_model.objects.create(
            name=position_name,
            args=args,
            priority_id=priority_id,
        )

        row.linked_jobs.set(position_job_ids)

        return True

    def position_edit(self, request) -> redirect:
        position_id = request.GET.get('id')

        if not position_id:
            messages.error(request, 'ID записи не указан.')
            return redirect(request.META.get('HTTP_REFERER'))

        row = self.position_model.objects.filter(id=position_id)

        if row.exists():
            row = row.first()
            position_name = request.POST.get('position-name')
            row.name = position_name

            position_oklad = request.POST.get('position-oklad')
            row.args["oklad"] = position_oklad

            position_all_storages = True if request.POST.get('position-all-storages') else False
            row.args["all_storages"] = position_all_storages

            position_is_usil = True if request.POST.get('position-is-usil') else False
            row.args["is_usil"] = position_is_usil

            position_is_called = True if request.POST.get('position-is-calling') else False
            row.args["is_called"] = position_is_called

            position_is_trainee = True if request.POST.get('position-is-trainee') else False
            row.args["is_trainee"] = position_is_trainee

            position_has_percent = True if request.POST.get('position-has-percent') else False
            row.args["has_percent"] = position_has_percent

            position_has_premium = True if request.POST.get('position-has-premium') else False
            row.args["has_premium"] = position_has_premium

            priority_id = request.POST.get('priority-id')
            row.priority_id = priority_id

            position_job_ids = request.POST.getlist('job_id')
            row.linked_jobs.set(position_job_ids)
            row.save()
            messages.success(request, 'Позиция успешно обновлена.')
        else:
            messages.error(request, 'Позиция не найдена.')

        return redirect('/lk/positions')

    def jobs_all(self) -> List[jobs_model]:
        return self.jobs_model.objects.all()

    def job_create(self, request) -> redirect:
        job_name = request.POST.get('job-name')
        job_oklad = None if request.POST.get('job-oklad') == '' else request.POST.get('job-oklad')

        self.jobs_model.objects.create(
            name=job_name,
            oklad=job_oklad
        )

        messages.success(request, 'Должность успешно добавлена :)')
        return redirect('/lk/jobs')

    def job_get(self, **kwargs) -> jobs_model:
        return self.jobs_model.objects.get(**kwargs)
