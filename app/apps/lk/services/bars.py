from apps.bar.models import Setting

from core import validators


def settings_edit(storage_id: int, percent: str, tg_chat_id: str):
    validators.validate_field(percent, 'процент')
    validators.validate_field(tg_chat_id, 'ID телеграм чата')

    settings = Setting.objects.filter(storage_id=storage_id)
    if settings.exists():
        settings = settings.first()
        settings.percent = percent
        settings.tg_chat_id = tg_chat_id
        settings.save()
    else:
        raise Setting.DoesNotExist('Запись с указанным идентификатором не найдена.')
