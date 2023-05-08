from django.db.models import Sum

from apps.bar.models import Timetable
from apps.lk.models import Fine

from global_services.salary import SalaryService

from typing import List


class TimetableService:
    model = Timetable

    def timetable_all(self) -> List[model]:
        return self.model.objects.all()

    def create(self, date_at: str, employee_id: int, storage_id: int, position_id: int, oklad: int) -> bool:
        timetable = self.model()
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
        timetable.fine = int(fine)
        timetable.save()

        return True
