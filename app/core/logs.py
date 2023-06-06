from typing import Union

from .tasks import create_log_task


def create_log(owner: str,  entity: str, row: Union, action: str, additional_data: str) -> None:
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
