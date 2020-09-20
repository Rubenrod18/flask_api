from flask_restx import fields

from app.extensions import api
from app.utils.swagger_models import CREATOR_SW_MODEL

USER_INPUT_SW_MODEL = api.model('UserInput', {
    'name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'email': fields.String(required=True),
    'genre': fields.String(required=True),
    'password': fields.String(required=True),
    'birth_date': fields.String(required=True),
    'role_id': fields.Integer(required=True),
})

USER_ROLE_OUTPUT_SW_MODEL = api.model('UserRoleOutput', {
    'name': fields.String(readonly=True),
    'label': fields.String(readonly=True),
})

USER_SW_MODEL = api.model('User', {
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
    'created_by': fields.Nested(CREATOR_SW_MODEL),
    'roles': fields.List(fields.Nested(USER_ROLE_OUTPUT_SW_MODEL))
})

USER_OUTPUT_SW_MODEL = api.model('UserOutput', {
    'data': fields.Nested(USER_SW_MODEL),
})

USER_SEARCH_OUTPUT_SW_MODEL = api.model('UserSearchOutput', {
    'data': fields.List(fields.Nested(USER_SW_MODEL)),
    'records_total': fields.Integer,
    'records_filtered': fields.Integer,
})
