from flask_restx import fields

from app.extensions import api


CREATOR_SW_MODEL = api.model('Creator', {
    'id': fields.Integer(),
})

_SEARCH_SEARCH_INPUT_SW_MODEL = api.model('SearchSearch', {
    'field_name': fields.String(required=True),
    'field_operator': fields.String(required=True),
    'field_value': fields.String(required=True,
                                 description='Could be string or integer.'),
})

_ORDER_DESCRIPTION = ('First value is the field name, second value is the '
                      'sort ( asc or desc ).')

SEARCH_INPUT_SW_MODEL = api.model('SearchInput', {
    'search': fields.List(fields.Nested(_SEARCH_SEARCH_INPUT_SW_MODEL,
                                        required=True)),
    'order': fields.List(fields.List(fields.String,
                                     description=_ORDER_DESCRIPTION,
                                     required=True),
                         example=[['name', 'asc'], ['size', 'desc']]),
    'items_per_page': fields.Integer(required=True),
    'page_number': fields.Integer(required=True),
})
