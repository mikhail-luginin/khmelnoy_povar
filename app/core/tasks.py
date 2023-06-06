from config.celery import app

from apps.lk.models import Log


@app.task
def create_log_task(owner: str,  entity: str, row: str, action: int, additional_data: str) -> None:
    Log.objects.create(
        owner=owner,
        entity=entity,
        row=row,
        action=action,
        additional_data=additional_data
    )
