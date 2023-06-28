from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect

from core import exceptions, validators
from core.services import positions_service
from core.services import storage_service
from core.utils.time import today_date

from apps.bar.models import Timetable
from apps.lk.models import Employee, EmployeeLog

import os
import secrets


def employees_with_deleted_filter(is_deleted: bool, **kwargs) -> list[Employee]:
    return Employee.objects.filter(is_deleted=0, **kwargs) if is_deleted is False else Employee.objects.filter(is_deleted=1, **kwargs)


def employees_all() -> list[Employee]:
    return Employee.objects.all()


def employee_get(employee_id) -> Employee:
    return Employee.objects.filter(id=employee_id).first()


@transaction.atomic()
def employee_create(request, first_name: str | None, last_name: str | None, birth_date: str | None, address: str | None,
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

    if Employee.objects.filter(phone__contains=phone[1:9]).exists():
        raise exceptions.UniqueFieldError('Данный номер телефона уже присутствует в базе сотрудников.')

    row = Employee(
        code=secrets.token_hex(16),
        photo=photo,
        fio=f'{last_name} {first_name}',
        birth_date=birth_date,
        address=address,
        job_place=positions_service.job_get(id=job_id),
        phone=phone,
        status=status
    )
    row.storage = storage_service.storage_get(id=storage_id) if storage_id is not None else storage_service.storage_get(
        code=request.GET.get('code'))
    row.save()

    EmployeeLog.objects.create(date_at=today_date(), employee=row, type=4, comment=description)

    return row


@transaction.atomic()
def employee_edit(employee_id: int | None, first_name: str | None, last_name: str | None,
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

    last_description = EmployeeLog.objects.filter(employee_id=employee_id, type=4).last()
    if not description:
        description = last_description.comment

    employee = Employee.objects.filter(id=employee_id).first()
    if employee:
        if int(status) != employee.status:
            validators.validate_field(status_change_comment, 'комментарий к изменению статуса')
            EmployeeLog.objects.create(date_at=today_date(), employee_id=employee_id, type=3,
                                       comment=f'{employee.get_status_display()} -> '
                                               f'{employee.get_status_by_id(int(status))}: {status_change_comment}')

        employee.fio = f'{last_name} {first_name}'
        employee.birth_date = birth_date
        employee.address = address
        employee.job_place_id = job_place_id
        employee.storage_id = storage_id
        employee.status = status

        old_photo = employee.photo
        if photo:
            employee.photo = photo
            if old_photo:
                if os.path.isfile(old_photo.path):
                    os.remove(old_photo.path)
        else:
            employee.photo = old_photo

        similar_employee = Employee.objects.filter(phone=phone).exclude(id=employee_id)
        if similar_employee.exists():
            raise exceptions.UniqueFieldError('Данный номер телефона уже присутствует в базе сотрудников.')
        else:
            employee.phone = phone
            employee.save()

        if last_description is None or (last_description and last_description.comment != description):
            EmployeeLog.objects.create(date_at=today_date(), employee_id=employee_id, type=4, comment=description)
    else:
        raise Employee.DoesNotExist('Запись с указанным идентификатором не найдена.')

    return employee


def dismiss(request) -> redirect:
    try:
        employee = Employee.objects.get(id=request.GET.get('id'))
    except Employee.DoesNotExist:
        messages.error(request, 'Сотрудник с данным ID не найден.')
        return redirect('/lk/employees')

    employee.is_deleted = 1
    employee.dismiss_date = today_date()
    # employee.dismiss_comment += ', ' + request.GET.get('comment')
    employee.save()

    messages.success(request, 'Сотрудник успешно уволен.')
    return redirect('/lk/employees')


def return_to_work(request) -> redirect:
    try:
        employee = Employee.objects.get(id=request.GET.get('id'))
    except Employee.DoesNotExist:
        messages.error(request, 'Сотрудник с данным ID не найден.')
        return redirect('/lk/employees')

    employee.is_deleted = 0
    employee.dismiss_date = None
    employee.save()

    messages.success(request, 'Сотрудник успешно возвращен.')
    return redirect('/lk/employees')


def last_work_day(employee_id: int):
    return Timetable.objects.filter(employee_id=employee_id).last()


def employee_logs(employee_id: int) -> list[EmployeeLog]:
    return EmployeeLog.objects.filter(employee_id=employee_id)
