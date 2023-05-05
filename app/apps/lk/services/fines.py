from apps.lk.models import Fine

from typing import List


class FineService:
    model = Fine

    def fines_all(self) -> List[model]:
        return self.model.objects.all()
