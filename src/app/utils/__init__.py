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
