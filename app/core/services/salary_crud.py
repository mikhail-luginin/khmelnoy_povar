from core import validators

from apps.bar.models import Salary


def create(date_at: str | None, salary_type: int | None, employee_id: int | None,
           storage_id: int | None, oklad: int | None, percent: int | None, premium: int | None,
           month: int | None, period: int | None) -> None:
    validators.validate_field(date_at, 'дата')
    validators.validate_field(salary_type, 'тип зарплаты')
    validators.validate_field(employee_id, 'сотрудник')
    validators.validate_field(storage_id, 'заведение')
    validators.validate_field(oklad, 'оклад')
    validators.validate_field(percent, 'процент')
    validators.validate_field(premium, 'премиум')

    salary = Salary.objects.create(date_at=date_at, type=salary_type, employee_id=employee_id,
                                   storage_id=storage_id, oklad=oklad, percent=percent, premium=premium)
    if salary_type == '2':
        salary.month = month
        salary.period = period
        salary.save()
    else:
        salary.month = None
        salary.period = None
        salary.save()


def edit(salary_id: int | None, date_at: str | None, salary_type: int | None, employee_id: int | None,
         storage_id: int | None, oklad: int | None, percent: int | None, premium: int | None,
         month: int | None, period: int | None) -> None:
    validators.validate_field(salary_id, 'идентификатор записи')
    validators.validate_field(date_at, 'дата')
    validators.validate_field(salary_type, 'тип зарплаты')
    validators.validate_field(employee_id, 'сотрудник')
    validators.validate_field(storage_id, 'заведение')
    validators.validate_field(oklad, 'оклад')
    validators.validate_field(percent, 'процент')
    validators.validate_field(premium, 'премиум')

    salary = Salary.objects.filter(id=salary_id).first()
    if salary:
        salary.date_at = date_at
        salary.type = salary_type
        salary.employee_id = employee_id
        salary.storage_id = storage_id
        salary.oklad = oklad
        salary.percent = percent
        salary.premium = premium
        salary.save()
    else:
        raise Salary.DoesNotExist('Запись с указанным идентификатором не найдена.')

    if salary_type == '2':
        salary.month = month
        salary.period = period
        salary.save()
    else:
        salary.month = None
        salary.period = None
        salary.save()
