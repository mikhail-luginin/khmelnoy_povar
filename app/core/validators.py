from . import exceptions


def validate_field(field, field_name: str) -> None:
    if not field:
        raise exceptions.FieldNotFoundError('Произошла ошибка. Перезагрузите страницу и попробуйте снова.')
    if field == '' or len(field) == 0:
        raise exceptions.FieldCannotBeEmptyError(f'Произошла ошибка. Поле "{field_name}" не может быть пустым.')
