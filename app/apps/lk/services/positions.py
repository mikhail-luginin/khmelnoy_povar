from django.shortcuts import redirect
from django.contrib import messages

from apps.lk.models import Position, JobPlace

from typing import List


class JobsService:
    position_model = Position
    jobs_model = JobPlace

    def positions_all(self) -> List[position_model]:
        return self.position_model.objects.all()

    def position_create(self, request) -> redirect:
        position_name = request.POST.get('position-name')
        position_oklad = request.POST.get('position-oklad')
        position_all_storages = True if request.POST.get('position-all-storages') is not None else False
        position_is_usil = True if request.POST.get('position-is-usil') is not None else False
        position_is_called = True if request.POST.get('position-is-calling') is not None else False
        position_is_trainee = True if request.POST.get('position-is-trainee') is not None else False
        position_has_percent = True if request.POST.get('position-has-percent') is not None else False
        position_has_premium = True if request.POST.get('position-has-premium') is not None else False
        position_job_ids = request.POST.getlist('job_id')

        priority_id = request.POST.get('priority-id')

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

        messages.success(request, 'Позиция успешно добавлена :)')
        return redirect('/lk/positions')

    def position_edit(self, request) -> redirect:
        position_id = request.GET.get('id')

        if not position_id:
            messages.error(request, 'ID записи не указан.')
            return redirect(request.META.get('HTTP_REFERER'))

        row = self.position_model.objects.get(id=position_id)

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
