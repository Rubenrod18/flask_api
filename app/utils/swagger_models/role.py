from flask_restx import fields

from app.extensions import api

ROLE_INPUT_SW_MODEL = api.model('RoleInput', {
    'name': fields.String(required=True),
    'description': fields.String,
    'label': fields.String(required=True),
})

ROLE_SW_MODEL = api.model('Role', {
    'id': fields.Integer(),
    'name': fields.String,
    'description': fields.String,
    'label': fields.String,
    'created_at': fields.String(),
    'updated_at': fields.String(),
    'deleted_at': fields.String(),
})

ROLE_OUTPUT_SW_MODEL = api.model('RoleOutput', {
    'data': fields.Nested(ROLE_SW_MODEL),
})

ROLE_SEARCH_OUTPUT_SW_MODEL = api.model('RoleSearchOutput', {
    'data': fields.List(fields.Nested(ROLE_SW_MODEL)),
    'records_total': fields.Integer,
    'records_filtered': fields.Integer,
})
