"""Collection of functions and classes which make common patterns
shorter and easier."""

from datetime import datetime


def to_readable(obj: object) -> object:
    if obj is None or obj == '':
        return 'N/D'
    elif isinstance(obj, datetime):
        return obj.strftime('%Y/%m/%d %H:%M:%S')
    else:
        return obj
