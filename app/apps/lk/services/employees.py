import secrets

from core.time import today_date
from core import validators
from apps.lk.models import Employee

from . import positions

from apps.iiko.services.storage import StorageService

from django.shortcuts import redirect
from django.contrib import messages

from typing import List


class EmployeeService:
    model = Employee

    def employees_all(self, is_deleted: bool, **kwargs) -> List[model]:
        return self.model.objects.all() if is_deleted is False else self.model.objects.filter(is_deleted=1, **kwargs)

    def employee_get(self, employee_id) -> model:
        return self.model.objects.get(id=employee_id)

    def employee_create(self, request) -> redirect:
        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        birth_date = request.POST.get('birth-date')
        address = request.POST.get('address')
        job_id = request.POST.get('job-id')
        storage_id = request.POST.get('storage-id')
        phone = request.POST.get('phone')

        if self.model.objects.filter(phone__contains=phone[1:9]).exists():
            messages.error(request, 'Данный сотрудник уже добавлен в базу.')
            return redirect(request.META.get('HTTP_REFERER'))

        row = self.model(
            photo=0,
            code=secrets.token_hex(16),
            fio=f'{last_name} {first_name}',
            birth_date=birth_date,
            address=address,
            job_place=positions.JobsService().job_get(id=job_id),
            phone=phone
        )
        row.storage = StorageService().storage_get(id=storage_id) if storage_id is not None else StorageService().storage_get(
            code=request.GET.get('code'))

        row.save()

        messages.success(request, 'Сотрудник успешно создан.')
        return redirect(request.META.get('HTTP_REFERER'))

    def employee_edit(self, employee_id: int | None, first_name: str | None, last_name: str | None,
                      birth_date: str | None, address: str | None, job_place_id: int | None,
                      storage_id: int | None, phone: str | None) -> None:
        validators.validate_field(employee_id, 'идентификатор записи')
        validators.validate_field(first_name, 'имя')
        validators.validate_field(last_name, 'фамилия')
        validators.validate_field(phone, 'телефон')
        validators.validate_field(job_place_id, 'должность')
        validators.validate_field(storage_id, 'заведение')

        employee = self.model.objects.filter(id=employee_id)
        if employee.exists():
            employee = employee.first()
            employee.fio = f'{last_name} {first_name}'
            employee.birth_date = birth_date
            employee.address = address
            employee.job_place_id = job_place_id
            employee.storage_id = storage_id

            similar_employee = self.model.objects.filter(phone=phone)
            if similar_employee.count() > 1:
                raise Exception('Данный номер телефона уже присутствует в базе сотрудников.')
            else:
                employee.phone = phone
                employee.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')

    def dismiss(self, request) -> redirect:
        try:
            employee = self.model.objects.get(id=request.GET.get('id'))
        except Employee.DoesNotExist:
            messages.error(request, 'Сотрудник с данным ID не найден.')
            return redirect('/lk/employees')

        employee.is_deleted = 1
        employee.dismiss_date = today_date()
        employee.save()

        messages.success(request, 'Сотрудник успешно уволен.')
        return redirect('/lk/employees')

    def return_to_work(self, request) -> redirect:
        try:
            employee = self.model.objects.get(id=request.GET.get('id'))
        except self.model.DoesNotExist:
            messages.error(request, 'Сотрудник с данным ID не найден.')
            return redirect('/lk/employees')

        employee.is_deleted = 0
        employee.dismiss_date = None
        employee.save()

        messages.success(request, 'Сотрудник успешно возвращен.')
        return redirect('/lk/employees')
