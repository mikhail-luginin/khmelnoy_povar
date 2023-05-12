from apps.bar.models import Setting

from core import exceptions


def settings_edit(percent: str | None) -> bool:
    settings = Setting.objects.get_or_create(id=1)

    if not percent:
        raise exceptions.FieldNotFoundError('Поле процент не найдено.')
    if percent == '0' or percent == '':
        raise exceptions.FieldCannotBeEmptyError('Поле процент не может быть пустым или равняться нулю.')

    settings.percent = percent
    settings.save()
    return True
