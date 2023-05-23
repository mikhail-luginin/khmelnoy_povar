from core import validators

from apps.lk.models import ItemDeficit, Profile


class ItemDeficitService:
    model = ItemDeficit

    def all(self):
        return self.model.objects.all()

    def deficit_by_storage(self, storage_id: int):
        return self.model.objects.filter(storage_id=storage_id)

    def create(self, storage_id: int | None, item: str | None, amount: str | None) -> None:
        validators.validate_field(item, 'предмет дефицита')
        validators.validate_field(amount, 'кол-во нехватки')

        self.model.objects.create(
            storage_id=storage_id,
            item=item,
            amount=amount,
            status=1
        )

    def send(self, request_id: int | None, user: Profile) -> bool:
        validators.validate_field(request_id, 'идентификатор запроса')

        request = self.model.objects.filter(id=request_id)
        if request.exists():
            request = request.first()

            if request.status != 1:
                return False
            else:
                request.owner = user
                request.status = 2
                request.save()
        else:
            raise self.model.DoesNotExist('Запрос с указанным идентификатором не найден.')

        return True

    def receive(self, request_id: int | None) -> bool:
        validators.validate_field(request_id, 'идентификатор запроса')

        request = self.model.objects.filter(id=request_id)
        if request.exists():
            request = request.first()

            if request.status != 2:
                return False
            else:
                request.status = 3
                request.save()
        else:
            raise self.model.DoesNotExist('Запрос с указанным идентификатором не найден.')

        return True
