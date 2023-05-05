from apps.bar.models import Salary

from typing import List


class SalaryService:
    model = Salary

    def salary_all(self) -> List[model]:
        return self.model.objects.all()
