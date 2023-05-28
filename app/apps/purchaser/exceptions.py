class DateIsNotEqualCurrentError(Exception):
    """
        Если дата не равна текущей.
    """


class RowWasNotCreatedByPurchaser(Exception):
    """
        Если запись не создана закупщиком.
    """
