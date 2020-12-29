from flask_restx import fields

from app.extensions import api
from app.swagger.core import creator_sw_model

user_input_sw_model = api.model('UserInput', {
    'name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'genre': fields.String(required=True),
    'password': fields.String(required=True),
    'birth_date': fields.String(required=True),
    'role_id': fields.Integer(required=True),
})

user_role_output_sw_model = api.model('UserRoleOutput', {
    'name': fields.String(readonly=True),
    'label': fields.String(readonly=True),
})

user_sw_model = api.model('User', {
    'id': fields.Integer(),
    'name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'genre': fields.String(enum=('m', 'f')),
    'birth_date': fields.String,
    'active': fields.Boolean,
    'created_at': fields.String(),
    'updated_at': fields.String(),
    'deleted_at': fields.String(),
    'created_by': fields.Nested(creator_sw_model),
    'roles': fields.List(fields.Nested(user_role_output_sw_model))
})

user_output_sw_model = api.model('UserOutput', {
    'data': fields.Nested(user_sw_model),
})

user_search_output_sw_model = api.model('UserSearchOutput', {
    'data': fields.List(fields.Nested(user_sw_model)),
    'records_total': fields.Integer,
    'records_filtered': fields.Integer,
})
