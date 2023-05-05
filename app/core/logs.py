from apps.lk.models import Logs


def create_log(username: str, page: str, action: str, comment: str = None, is_bar: bool = False) -> None:
    Logs.objects.create(
        username=username,
        page=page,
        action=action,
        comment=comment,
        is_bar=is_bar
    )

# ToDo: Celery integration
