from apps.bar.models import Setting

from core import exceptions


def settings_edit(percent: str | None):
    settings = Setting.objects.filter(id=1)

    if not percent:
        raise exceptions.FieldNotFoundError('Поле процент не найдено.')
    if percent == '0' or percent == '':
        raise exceptions.FieldCannotBeEmptyError('Поле процент не может быть пустым или равняться нулю.')

    if settings.exists():
        settings = settings.first()
        settings.percent = percent
        settings.save()
    else:
        raise Setting.DoesNotExist(f'Запись в справочнике с идентификатором {settings.id} не найдена.')