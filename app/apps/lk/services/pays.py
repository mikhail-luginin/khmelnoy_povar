from apps.bar.models import Pays

from typing import List


class PaysService:
    model = Pays

    def pays_all(self) -> List[model]:
        return self.model.objects.all()
