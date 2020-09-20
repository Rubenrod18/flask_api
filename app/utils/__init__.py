import importlib
import operator
from datetime import date, datetime
from functools import reduce
from typing import Type

from peewee import CharField, ModelSelect, TextField, FixedCharField, UUIDField, Model, Field

BIRTH_DATE_REGEX = (r'^(19[0-9]{2}|2[0-9]{3})'  # Year
                    r'-(0[1-9]|1[012])'  # Month
                    r'-([123]0|[012][1-9]|31)$')  # Day
EMAIL_REGEX = (r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
TOKEN_REGEX = r'^Bearer\s(\S+)$'

# http://docs.peewee-orm.com/en/latest/peewee/query_operators.html
QUERY_OPERATORS = [
    'eq', 'ne',
    'lt', 'lte',
    'gt', 'gte',
    'in', 'nin',
    'between',
]

STRING_QUERY_OPERATORS = [
    'eq', 'ne',
    'contains', 'ncontains',
    'startswith', 'endswith',
]

"""
    REQUEST_QUERY_DELIMITER is used for converting requests field values to a list, for example:
        Request send these values:
            field_operator: contains
            field_values: valueA;valueB;valueC
        
        The delimiter operator splits values to a list of values:
            field_values: [valueA, valueB, valueC]
"""
REQUEST_QUERY_DELIMITER = ';'


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


def _build_order_by(db_model: Type[Model], request_data: dict) -> list:
    order_by_values = []
    request_order = request_data.get('order', [['id', 'asc']])

    if isinstance(request_order, list):
        for item in request_order:
            field_name, sort = item
            field = db_model._meta.fields[field_name]
            order_by = getattr(field, sort)()

            order_by_values.append(order_by)

    return order_by_values


def get_request_query_fields(db_model: Type[Model], request_data=None) -> tuple:
    request_data = request_data or {}

    # Page numbers are 1-based, so the first page of results will be page 1.
    # http://docs.peewee-orm.com/en/latest/peewee/querying.html#paginating-records
    page_number = int(request_data.get('page_number', 1))
    items_per_page = int(request_data.get('items_per_page', 10))
    order_by = _build_order_by(db_model, request_data)

    return page_number, items_per_page, order_by


def _build_string_clause(field: Field, field_operator: str, field_value) -> tuple:
    sql_clause = ()

    if field_value.find(REQUEST_QUERY_DELIMITER) != -1:
        field_value = field_value.split(REQUEST_QUERY_DELIMITER)
        sql_clauses = []

        for item in field_value:
            sql_clauses.append(_build_string_clause(field, field_operator, item))

        sql_clause = reduce(operator.or_, sql_clauses)
    elif field_operator in STRING_QUERY_OPERATORS:
        if field_operator == 'eq':
            sql_clause = (field == field_value)
        elif field_operator == 'neq':
            sql_clause = (~(field == field_value))
        elif field_operator == 'contains':
            sql_clause = (field.contains(field_value))
        elif field_operator == 'ncontains':
            sql_clause = (~(field.contains(field_value)))
        elif field_operator == 'startswith':
            sql_clause = (field.startswith(field_value))
        elif field_operator == 'endswith':
            sql_clause = (field.endswith(field_value))

    return sql_clause


def _build_clause_operators(field: Field, field_operator: str, field_value) -> tuple:
    sql_clause = ()

    if isinstance(field_value, str) and field_value.find(REQUEST_QUERY_DELIMITER) != -1:
        field_value = field_value.split(REQUEST_QUERY_DELIMITER)
        sql_clauses = []

        for item in field_value:
            sql_clauses.append(_build_clause_operators(field, field_operator, item))

        sql_clause = reduce(operator.or_, sql_clauses)
    elif field_operator in QUERY_OPERATORS:
        if field_operator == 'eq':
            sql_clause = (field == field_value)
        elif field_operator == 'ne':
            sql_clause = (field != field_value)
        elif field_operator == 'lt':
            sql_clause = (field < field_value)
        elif field_operator == 'lte':
            sql_clause = (field <= field_value)
        elif field_operator == 'gt':
            sql_clause = (field > field_value)
        elif field_operator == 'gte':
            sql_clause = (field >= field_value)
        elif field_operator == 'in':
            sql_clause = (field.in_(field_value.split(REQUEST_QUERY_DELIMITER)))
        elif field_operator == 'nin':
            sql_clause = (field.not_in(field_value))
        elif field_operator == 'between':
            values = field_value.split(REQUEST_QUERY_DELIMITER)
            sql_clause = (field.between(low=values[0], high=values[1]))

    return sql_clause


def _build_query_clause(field: Field, field_operator: str, field_value):
    is_string_field = (
            isinstance(field, CharField) |
            isinstance(field, FixedCharField) |
            isinstance(field, TextField) |
            isinstance(field, UUIDField)
    )

    if is_string_field:
        sql_clause = _build_string_clause(field, field_operator, field_value)
    else:
        sql_clause = _build_clause_operators(field, field_operator, field_value)

    return sql_clause


def create_search_query(db_model: Type[Model], query: ModelSelect, data: dict = None) -> ModelSelect:
    if data is None:
        data = {}

    filters = data.get('search', {})

    sql_clauses = []

    for filter in filters:
        field_name = filter['field_name']
        field = db_model._meta.fields[field_name]

        field_operator = filter['field_operator']
        field_value = filter['field_value']

        if isinstance(field_value, str) and not field_value.strip():
            continue

        sql_clause = _build_query_clause(field, field_operator, field_value)
        sql_clauses.append(sql_clause)

    if sql_clauses:
        query = query.where(*sql_clauses)

    return query
