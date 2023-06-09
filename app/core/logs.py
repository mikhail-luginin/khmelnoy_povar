from apps.lk.models import Log

from .tasks import create_log_task

from typing import Union

import datetime


def create_log(owner: str, entity: str, row: Union, action: str, additional_data: str) -> None:
    match action:
        case 'create':
            action = 1
        case 'edit':
            action = 2
        case 'delete':
            action = 3
        case 'update':
            action = 4
        case 'copy':
            action = 5
    row = f'{type(row).__name__} {row.id}'
    create_log_task.delay(owner=owner, entity=entity, row=row, action=action, additional_data=additional_data)


class LogsService:

    def update(self, timestamp: str | None) -> list[dict]:
        if timestamp:
            timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ') + datetime.timedelta(hours=3)
            logs_queryset = Log.objects.filter(created_at__gte=timestamp - datetime.timedelta(seconds=5))
        else:
            logs_queryset = Log.objects.all()

        return [{
            "created_at": log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "owner": log.owner,
            "entity": log.entity,
            "row": log.row,
            "action_name": log.get_action_display(),
            "additional_data": log.additional_data,
            "action": log.action
        } for log in logs_queryset]
