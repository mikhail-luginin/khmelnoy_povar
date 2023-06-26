import os
import secrets

from apps.bar.models import Timetable
from core import exceptions
from core.utils.time import today_date
from core import validators
from apps.lk.models import Employee

from core.services import positions

from core.services.storage import StorageService

from django.shortcuts import redirect
from django.contrib import messages


class EmployeeService:
    model = Employee

    def employees_all(self, is_deleted: bool, **kwargs) -> list[model]:
        return self.model.objects.filter(is_deleted=0, **kwargs) if is_deleted is False else self.model.objects.filter(is_deleted=1, **kwargs)

    def all(self):
        return self.model.objects.all()

    def employee_get(self, employee_id) -> model:
        return self.model.objects.filter(id=employee_id).first()

    def employee_create(self, request, first_name: str | None, last_name: str | None, birth_date: str | None, address: str | None,
                        job_id: int | None, storage_id: int | None, phone: str | None, status: int | None, photo,
                        description: str | None) -> Employee:
        validators.validate_field(first_name, 'фамилия')
        validators.validate_field(last_name, 'имя')
        validators.validate_field(birth_date, 'дата рождения')
        validators.validate_field(phone, 'номер телефона')

        job_id = None if job_id == '' else job_id
        storage_id = None if storage_id == '' else storage_id
        status = 3 if status == '' else status

        if not photo:
            photo = None

        if '_' in phone:
            raise exceptions.IncorrectFieldError('Некорректный ввод номера телефона. Попробуйте еще раз.')

        if self.model.objects.filter(phone__contains=phone[1:9]).exists():
            raise exceptions.UniqueFieldError('Данный номер телефона уже присутствует в базе сотрудников.')

        row = self.model(
            code=secrets.token_hex(16),
            photo=photo,
            fio=f'{last_name} {first_name}',
            birth_date=birth_date,
            address=address,
            job_place=positions.JobsService().job_get(id=job_id),
            phone=phone,
            status=status,
            description=description
        )
        row.storage = StorageService().storage_get(id=storage_id) if storage_id is not None else StorageService().storage_get(
            code=request.GET.get('code'))
        row.save()

        return row

    def employee_edit(self, employee_id: int | None, first_name: str | None, last_name: str | None,
                      birth_date: str | None, address: str | None, job_place_id: int | None,
                      storage_id: int | None, phone: str | None, status: int | None, photo,
                      description: str | None, status_change_comment: str | None) -> Employee:
        validators.validate_field(first_name, 'фамилия')
        validators.validate_field(last_name, 'имя')
        validators.validate_field(birth_date, 'дата рождения')
        validators.validate_field(phone, 'номер телефона')
        validators.validate_field(job_place_id, 'должность')
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(status, 'статус')

        if len(phone) != 10:
            raise exceptions.IncorrectFieldError('Некорректный ввод номера телефона. Попробуйте еще раз')

        employee = self.model.objects.filter(id=employee_id).first()

        if employee:
            if int(status) != employee.status:
                validators.validate_field(status_change_comment, 'Комментарий к изменению статуса')
                employee.status_change_comment += ' / ' + status_change_comment

            employee.fio = f'{last_name} {first_name}'
            employee.birth_date = birth_date
            employee.address = address
            employee.job_place_id = job_place_id
            employee.storage_id = storage_id
            employee.status = status
            employee.description = description

            old_photo = employee.photo

            if photo:
                employee.photo = photo
                if old_photo:
                    if os.path.isfile(old_photo.path):
                        os.remove(old_photo.path)
            else:
                employee.photo = old_photo

            similar_employee = self.model.objects.filter(phone=phone).exclude(id=employee_id)
            if similar_employee.exists():
                raise exceptions.UniqueFieldError('Данный номер телефона уже присутствует в базе сотрудников.')
            else:
                employee.phone = phone
                employee.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')

        return employee

    def dismiss(self, request) -> redirect:
        try:
            employee = self.model.objects.get(id=request.GET.get('id'))
        except Employee.DoesNotExist:
            messages.error(request, 'Сотрудник с данным ID не найден.')
            return redirect('/lk/employees')

        employee.is_deleted = 1
        employee.dismiss_date = today_date()
        employee.dismiss_comment += ', ' + request.GET.get('comment')
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

    def last_work_date(self, employee_id: int):
        return Timetable.objects.filter(id=employee_id).order_by('-date_at').first()
