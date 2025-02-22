"""Collection of functions and classes which make common patterns
shorter and easier."""

import logging
from datetime import date, datetime

logger = logging.getLogger(__name__)


def to_readable(obj: object) -> object:
    if obj is None or obj == '':
        return 'N/D'
    elif isinstance(obj, datetime):
        return obj.strftime('%Y/%m/%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.__str__()
    else:
        return obj


def pos_to_char(pos: int) -> str:
    return chr(pos + 97)


def ignore_keys(data: dict, exclude: list) -> dict:
    return dict({item: data[item] for item in data if item not in exclude})


def filter_by_keys(data: dict, keys: list) -> dict:
    return {key: value for key, value in data.items() if key in keys}
