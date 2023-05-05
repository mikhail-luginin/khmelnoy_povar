from apps.bar.models import Timetable

from typing import List


class TimetableService:
    model = Timetable

    def timetable_all(self) -> List[model]:
        return self.model.objects.all()
