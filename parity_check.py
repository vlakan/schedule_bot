import calendar
from datetime import datetime as dt
from datetime import timedelta


def parity_checker(date=None):
    if date is None:
        date = dt.now()
    reference_date = dt(day=1, month=9, year=2022)

    wday = calendar.weekday(reference_date.year, reference_date.month, reference_date.day)
    day = calendar.day_name[wday]

    while day != 'Monday':
        reference_date -= timedelta(1)
        wday = calendar.weekday(reference_date.year, reference_date.month, reference_date.day)
        day = calendar.day_name[wday]

    reference_date -= timedelta(7)
    delta = date - reference_date
    count_days = delta.days // 7

    if count_days % 2 == 0:
        return 'Четная неделя'
    else:
        return 'Нечетная неделя'
