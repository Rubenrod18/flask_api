from flask_restx import fields

from app.extensions import api
from app.swagger.core import creator_sw_model, record_monitoring_sw_model

user_input_sw_model = api.model(
    'UserInput',
    {
        'name': fields.String(required=True),
        'last_name': fields.String(required=True),
        'email': fields.String(required=True),
        'genre': fields.String(required=True),
        'password': fields.String(required=True),
        'birth_date': fields.String(required=True),
        'role_id': fields.Integer(required=True),
    },
)

_user_role_output_sw_model = api.model(
    'UserRoleOutput',
    {
        'name': fields.String(readonly=True),
        'label': fields.String(readonly=True),
    },
)

user_sw_model = api.clone(
    'User',
    record_monitoring_sw_model,
    {
        'created_by': fields.Nested(creator_sw_model),
        'roles': fields.List(fields.Nested(_user_role_output_sw_model)),
        'name': fields.String,
        'last_name': fields.String,
        'email': fields.String,
        'genre': fields.String(enum=('m', 'f')),
        'birth_date': fields.String,
        'active': fields.Boolean,
    },
)

user_search_output_sw_model = api.model(
    'UserSearchOutput',
    {
        'data': fields.List(fields.Nested(user_sw_model)),
        'records_total': fields.Integer,
        'records_filtered': fields.Integer,
    },
)
