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
        Введенный тип данных не подходит под поле модели.
    """


class UniqueFieldError(Exception):
    """
        Такая запись уже есть в справочнике.
    """


class IncorrectFieldError(Exception):
    """
        Некорректный ввод.
    """
