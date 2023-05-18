class FieldNotFoundError(Exception):
    """
        Если поле не найдено.
    """


class FieldCannotBeEmptyError(Exception):
    """
        Поле не может быть пустым.
    """


class EmployeeCanNotBeDeletedError(Exception):
    """
        Если сотрудник не уволен.
    """