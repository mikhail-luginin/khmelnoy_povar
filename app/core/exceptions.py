class FieldNotFoundError(Exception):
    """
        Если поле не найдено.
    """


class FieldCannotBeEmptyError(Exception):
    """
        Поле не может быть пустым.
    """

class WrongFieldTypeError(ValueError):
    """
        Введенный тип данных не подходит под поле модели
    """
