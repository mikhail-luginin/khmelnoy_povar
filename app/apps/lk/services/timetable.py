from django.db.models import Sum

from core import validators

from apps.bar.models import Timetable
from apps.lk.models import Fine

from global_services.salary import SalaryService

from typing import List


class TimetableService:
    model = Timetable

    def timetable_all(self) -> List[model]:
        return self.model.objects.all()

    def create(self, date_at: str | None, employee_id: int | None,
               storage_id: int | None, position_id: int | None, oklad: int | None) -> None:
        validators.validate_field(date_at, 'дата')
        validators.validate_field(employee_id, 'сотрудник')
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(position_id, 'позиция')
        validators.validate_field(oklad, 'оклад')

        timetable = self.model.objects.create(date_at=date_at, employee_id=employee_id,
                                              storage_id=storage_id, position_id=position_id, oklad=oklad)

        money_data = SalaryService().calculate_prepayment_salary_by_timetable_object(timetable_object=timetable)

        timetable.percent = money_data['percent']
        timetable.premium = money_data['premium']

        fine = Fine.objects.filter(employee_id=employee_id, date_at=date_at).aggregate(Sum("sum"))['sum__sum']
        timetable.fine = int(fine)
        timetable.save()

    def edit(self, timetable_id: int | None, date_at: str | None, employee_id: int | None,
             storage_id: int | None, position_id: int | None, oklad: int | None) -> None:
        validators.validate_field(timetable_id, 'идентификатор записи')
        validators.validate_field(date_at, 'дата')
        validators.validate_field(employee_id, 'сотрудник')
        validators.validate_field(storage_id, 'заведение')
        validators.validate_field(position_id, 'позиция')
        validators.validate_field(oklad, 'оклад')

        timetable = self.model.objects.filter(id=timetable_id)
        if timetable.exists():
            timetable = timetable.first()
            timetable.date_at = date_at
            timetable.employee_id = employee_id
            timetable.storage_id = storage_id
            timetable.position_id = position_id
            timetable.oklad = oklad
            timetable.save()

            money_data = SalaryService().calculate_prepayment_salary_by_timetable_object(timetable_object=timetable)

            timetable.percent = money_data['percent']
            timetable.premium = money_data['premium']

            fine = Fine.objects.filter(employee_id=employee_id, date_at=date_at).aggregate(Sum("sum"))['sum__sum']
            timetable.fine = int(fine) if fine is not None else 0
            timetable.save()
        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')

    def is_employee_work_on_date(self, employee_id: int, date_at: str) -> bool:
        return self.model.objects.filter(employee_id=employee_id, date_at=date_at).exists()
