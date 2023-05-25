from apps.bar.models import Timetable
from core import validators

from apps.lk.models import Fine

from typing import List


class FineService:
    model = Fine

    def fines_all(self) -> List[model]:
        return self.model.objects.all()

    def create(self, date_at: str | None, employee_id: int | None,
               fine_sum: int | None, reason_id: int | None) -> None:
        validators.validate_field(date_at, 'дата')
        validators.validate_field(employee_id, 'сотрудник')
        validators.validate_field(fine_sum, 'сумма')
        validators.validate_field(reason_id, 'причина')

        self.model.objects.create(
            date_at=date_at,
            employee_id=employee_id,
            sum=fine_sum,
            reason_id=reason_id
        )

        timetable = Timetable.objects.filter(date_at=date_at, employee_id=employee_id)
        if timetable.exists():
            timetable = timetable.first()
            timetable.fine += int(fine_sum)
            timetable.save()

    def edit(self, fine_id: int | None, date_at: str | None,
             employee_id: int | None, fine_sum: int | None, reason_id: int | None) -> None:
        validators.validate_field(fine_id, 'идентификатор записи')
        validators.validate_field(date_at, 'дата')
        validators.validate_field(employee_id, 'сотрудник')
        validators.validate_field(fine_sum, 'сумма')
        validators.validate_field(reason_id, 'причина')

        fine = self.model.objects.filter(id=fine_id)
        if fine.exists():
            fine = fine.first()
            timetable = Timetable.objects.filter(date_at=date_at, employee_id=employee_id)
            if timetable.exists():
                timetable = timetable.first()
                timetable.fine -= fine.sum
                if int(fine_sum) == 0:
                    timetable.fine = 0
                else:
                    timetable.fine += int(fine_sum)

                timetable.save()

            fine.date_at = date_at
            fine.employee_id = employee_id
            fine.sum = fine_sum
            fine.reason_id = reason_id
            fine.save()

        else:
            raise self.model.DoesNotExist('Запись с указанным идентификатором не найдена.')

    def delete(self, fine_id: int):
        fine = self.model.objects.filter(id=fine_id)
        if fine.exists():
            fine = fine.first()

            timetable = self.model.objects.filter(employee=fine.employee, date_at=fine.date_at)
            if timetable.exists():
                timetable = timetable.first()
                timetable.fine -= fine.sum
                timetable.save()

            fine.delete()
