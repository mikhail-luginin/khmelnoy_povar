class FieldNotFoundError(Exception):
    """
        Если поле не найдено.
    """


class FieldCannotBeEmptyError(Exception):
    """
        Поле не может быть пустым.
    """
