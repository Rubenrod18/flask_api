from flask_restx import fields

from app.extensions import api

creator_sw_model = api.model('Creator', {
    'id': fields.Integer(readonly=True, example=3),
})

record_monitoring_sw_model = api.model('RecordMonitoring', {
    'id': fields.Integer(readonly=True, example=1),
    'created_at': fields.String(readonly=True, example='2000-01-01 00:00:00'),
    'updated_at': fields.String(readonly=True, example='2000-01-01 00:00:00'),
    'deleted_at': fields.String(readonly=True, example='2000-01-01 00:00:00'),
})

_field_operator_description = """
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

_search_search_input_sw_model = api.model('SearchSearch', {
    'field_name': fields.String(required=True, example='name'),
    'field_operator': fields.String(required=True,
                                    description=_field_operator_description,
                                    example='contains'),
    'field_value': fields.String(required=True,
                                 description='Could be string or integer.',
                                 example='n'),
})

_order_input_sw_model = api.model('SearchOrderInput', {
    'field_name': fields.String(required=True),
    'sorting': fields.String(required=True, enum=['asc', 'desc'])
})

_order_description = ('First value is the field name, second value is the '
                      'sort ( asc or desc ).')

search_input_sw_model = api.model('SearchInput', {
    'search': fields.List(fields.Nested(_search_search_input_sw_model,
                                        required=True)),
    'order': fields.List(fields.Nested(_order_input_sw_model,
                                       description=_order_description,
                                       required=True),
                         example=[
                             {'field_name': 'name', 'sorting': 'asc'},
                             {'field_name': 'created_at', 'sorting': 'desc'}
                         ]),
    'items_per_page': fields.Integer(required=True, example=10),
    'page_number': fields.Integer(required=True, example=1),
})
