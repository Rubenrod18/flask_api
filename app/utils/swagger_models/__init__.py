from flask_restx import fields

from app.extensions import api


CREATOR_SW_MODEL = api.model('Creator', {
    'id': fields.Integer(),
})

_FIELD_OPERATOR_DESCRIPTION = """
general type query operators:
&emsp;&emsp;&emsp;&emsp; eq: x equals to field_value. 

&emsp;&emsp;&emsp;&emsp; ne: x not equals to field_value.

&emsp;&emsp;&emsp;&emsp; lt: x less than field_value.

&emsp;&emsp;&emsp;&emsp; lte: x less than or equal to field_value.

&emsp;&emsp;&emsp;&emsp; gt: x great than field_value.

&emsp;&emsp;&emsp;&emsp; gte: x great than or equal to field_value.

&emsp;&emsp;&emsp;&emsp; in: x is in list field_value.

&emsp;&emsp;&emsp;&emsp; nin: x is not in list field_value.

&emsp;&emsp;&emsp;&emsp; between: x between field_value. For example: "1;10"

string type query operators:
&emsp;&emsp;&emsp;&emsp; eq: x equals to field_value.

&emsp;&emsp;&emsp;&emsp; ne: x no equals to field_value.

&emsp;&emsp;&emsp;&emsp; contains: x contains field_value.

&emsp;&emsp;&emsp;&emsp; ncontains: x no contains field_value.

&emsp;&emsp;&emsp;&emsp; startswith: x starts with field_value.

&emsp;&emsp;&emsp;&emsp; endswith: x ends with field_value.
"""

_SEARCH_SEARCH_INPUT_SW_MODEL = api.model('SearchSearch', {
    'field_name': fields.String(required=True, example='name'),
    'field_operator': fields.String(required=True,
                                    description=_FIELD_OPERATOR_DESCRIPTION,
                                    example='contains'),
    'field_value': fields.String(required=True,
                                 description='Could be string or integer.',
                                 example='n'),
})

_ORDER_DESCRIPTION = ('First value is the field name, second value is the '
                      'sort ( asc or desc ).')

SEARCH_INPUT_SW_MODEL = api.model('SearchInput', {
    'search': fields.List(fields.Nested(_SEARCH_SEARCH_INPUT_SW_MODEL,
                                        required=True)),
    'order': fields.List(fields.List(fields.String,
                                     description=_ORDER_DESCRIPTION,
                                     required=True),
                         example=[['name', 'asc'], ['created_at', 'desc']]),
    'items_per_page': fields.Integer(required=True, example=10),
    'page_number': fields.Integer(required=True, example=1),
})
