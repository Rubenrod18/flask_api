# Regex
BIRTH_DATE_REGEX = r'^(19[0-9]{2}|2[0-9]{3})-(0[1-9]|1[012])-([123]0|[012][1-9]|31)$'
EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

# Auth
TOKEN_REGEX = r'^Bearer\s(\S+)$'

# Files
PDF_MIME_TYPE = 'application/pdf'
MS_WORD_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
MS_EXCEL_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

# Request query operator
"""
    REQUEST_QUERY_DELIMITER is used for converting requests field
    values to a list, for example:
        Request send these values:
            field_operator: contains
            field_values: valueA;valueB;valueC

        The delimiter operator splits values to a list of values:
            field_values: [valueA, valueB, valueC]
"""
REQUEST_QUERY_DELIMITER = ';'
STRING_QUERY_OPERATORS = [
    'eq',
    'ne',
    'contains',
    'ncontains',
    'startswith',
    'endswith',
]
# http://docs.peewee-orm.com/en/latest/peewee/query_operators.html
QUERY_OPERATORS = [
    'eq',
    'ne',
    'lt',
    'lte',
    'gt',
    'gte',
    'in',
    'nin',
    'between',
]
