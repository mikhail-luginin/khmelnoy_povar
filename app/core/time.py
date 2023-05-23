import datetime

import calendar

from typing import Union, Dict


def get_current_time() -> datetime.date:
    delta = datetime.timedelta(hours=3, minutes=0)
    return datetime.datetime.now(datetime.timezone.utc) - delta


def today_date() -> str:
    return get_current_time().strftime('%Y-%m-%d')


def today_datetime() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def monthdelta(date: datetime, delta: int) -> datetime.date:
    m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, calendar.monthrange(y, m)[1])
    return date.replace(day=d, month=m, year=y)


def get_months(month_id: int = None) -> Union[Dict[int, str], str]:
    months = {
        1: 'Январь',
        2: 'Февраль',
        3: 'Март',
        4: 'Апрель',
        5: 'Май',
        6: 'Июнь',
        7: 'Июль',
        8: 'Август',
        9: 'Сентябрь',
        10: 'Октябрь',
        11: 'Ноябрь',
        12: 'Декабрь',
    }

    return months if month_id is None else months.get(month_id, "")
