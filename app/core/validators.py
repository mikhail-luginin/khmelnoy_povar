from . import exceptions


def validate_field(field, field_name: str) -> None:
    if not field:
        raise exceptions.FieldNotFoundError(f'Произошла ошибка. Поле "{field_name}" не может быть пустым.')
