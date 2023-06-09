from core import validators

from apps.lk.models import ItemDeficit, Profile
from core.logs import create_log
from core.utils.telegram import send_message_to_telegram
from core.utils.time import today_datetime


def item_deficit_all():
    return ItemDeficit.objects.all()


def deficit_by_storage(storage_id: int):
    return ItemDeficit.objects.filter(storage_id=storage_id)


def create(storage_id: int | None, item: str | None, amount: str | None) -> None:
    validators.validate_field(item, 'предмет дефицита')
    validators.validate_field(amount, 'кол-во нехватки')

    row = ItemDeficit.objects.create(
        created_at=today_datetime(),
        storage_id=storage_id,
        item=item,
        amount=amount,
        status=1
    )
    send_message_to_telegram('-914595897', f'<b>[{row.storage.name}]</b> Добавлена нехватка: {item} ({amount})')
    create_log(owner=f'CRM {row.storage.name}', entity=row.storage.name, row=row,
               action='create', additional_data='Нехватка создана')


def send(request_id: int | None, user: Profile, sended_amount: int, comment: str | None) -> bool:
    validators.validate_field(request_id, 'идентификатор запроса')
    validators.validate_field(sended_amount, 'кол-во отправленного предмета')

    request = ItemDeficit.objects.filter(id=request_id).first()
    if request:
        if request.status != 1:
            return False
        else:
            request.owner = user
            request.sended_amount = sended_amount
            if comment:
                request.comment = comment
            request.status = 2
            request.save()
    else:
        raise ItemDeficit.DoesNotExist('Запрос с указанным идентификатором не найден.')

    return True


def receive(request_id: int | None, arrived_amount: int, comment: str | None) -> bool:
    validators.validate_field(request_id, 'идентификатор запроса')

    request = ItemDeficit.objects.filter(id=request_id).first()
    if request:
        if request.status != 2:
            return False
        else:
            request.receive_date = today_datetime()
            request.arrived_amount = arrived_amount
            if comment:
                request.comment += ' / ' + comment
            request.status = 3
            request.save()
            create_log(owner=f'CRM {request.storage.name}', entity=request.storage.name, row=request,
                       action='edit', additional_data='Нехватка получена')
    else:
        raise ItemDeficit.DoesNotExist('Запрос с указанным идентификатором не найден.')

    return True
