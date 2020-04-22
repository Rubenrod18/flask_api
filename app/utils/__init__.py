from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def to_readable(obj: object) -> object:
    if obj is None or obj == '':
        return 'N/D'
    elif isinstance(obj, datetime):
        return obj.strftime('%Y/%m/%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.__str__()
    else:
        return obj


def difference_in_years(start_date: object, end_date: object) -> int:
    return relativedelta(end_date, start_date).years
