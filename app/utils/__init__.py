import importlib
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

BIRTH_DATE_REGEX = (r'^(19[0-9]{2}|2[0-9]{3})'  # Year
                    r'-(0[1-9]|1[012])'  # Month
                    r'-([123]0|[012][1-9]|31)$')  # Day
EMAIL_REGEX = (r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')


def class_for_name(module_name: str, class_name: str) -> object:
    # load the module, will raise ImportError if module cannot be loaded
    m = importlib.import_module(module_name)
    # get the class, will raise AttributeError if class cannot be found
    c = getattr(m, class_name)
    return c


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


def pos_to_char(pos: int) -> str:
    return chr(pos + 97)


def find_longest_word(word_list: list) -> str:
    str_list = [str(item) for item in word_list]
    longest_word = max(str_list, key=len)
    return str(longest_word)
