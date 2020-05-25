import importlib
from datetime import date, datetime

from peewee import IntegerField, CharField, DateField, DateTimeField, ModelSelect

BIRTH_DATE_REGEX = (r'^(19[0-9]{2}|2[0-9]{3})'  # Year
                    r'-(0[1-9]|1[012])'  # Month
                    r'-([123]0|[012][1-9]|31)$')  # Day
EMAIL_REGEX = (r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
TOKEN_REGEX = r'^Bearer\s(\S+)$'


class FileEmptyError(OSError):
    pass


def class_for_name(module_name: str, class_name: str) -> any:
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


def pos_to_char(pos: int) -> str:
    return chr(pos + 97)


def find_longest_word(word_list: list) -> str:
    str_list = [str(item) for item in word_list]
    longest_word = max(str_list, key=len)
    return str(longest_word)


def ignore_keys(data: dict, exclude: list) -> dict:
    return dict({
        item: data[item]
        for item in data
        if item not in exclude
    })


def get_request_query_fields(db_model, request_data=None) -> tuple:
    if request_data is None:
        request_data = {}

    # Page numbers are 1-based, so the first page of results will be page 1.
    # http://docs.peewee-orm.com/en/latest/peewee/querying.html#paginating-records
    tmp = int(request_data.get('page_number', 1))
    page_number = 1 if tmp < 1 else tmp

    tmp = int(request_data.get('items_per_page', 10))
    items_per_page = 10 if tmp < 1 else tmp

    sort = request_data.get('sort', 'id')
    order = request_data.get('order', 'asc')

    order_by = db_model._meta.fields[sort]

    if order == 'desc':
        order_by = order_by.desc()

    return (page_number, items_per_page, order_by,)


def create_query(db_model, query: ModelSelect = ModelSelect, data: dict = None) -> ModelSelect:
    if data is None:
        data = {}

    search_data = data.get('search', {})

    filters = [
        item for item in search_data
        if 'field_value' in item and item.get('field_value') != ''
    ]

    for filter in filters:
        field_name = filter['field_name']
        field = db_model._meta.fields[field_name]

        field_value = filter['field_value']

        if isinstance(field, IntegerField):
            query = query.where(field == field_value)
        elif isinstance(field, CharField):
            field_value = field_value.__str__()
            value = '%{0}%'.format(field_value)
            # OR use the exponent operator.
            # Note: you must include wildcards here:
            query = query.where(field ** value)
        elif isinstance(field, DateField):
            # TODO: WIP -> add field_operator
            pass
        elif isinstance(field, DateTimeField):
            # TODO: add field_operator
            pass

    return query
