from flask_restx import fields

from app.extensions import api

role_input_sw_model = api.model('RoleInput', {
    'name': fields.String(required=True),
    'description': fields.String,
    'label': fields.String(required=True),
})

role_sw_model = api.model('Role', {
    'id': fields.Integer(),
    'name': fields.String,
    'description': fields.String,
    'label': fields.String,
    'created_at': fields.String(),
    'updated_at': fields.String(),
    'deleted_at': fields.String(),
})

role_output_sw_model = api.model('RoleOutput', {
    'data': fields.Nested(role_sw_model),
})

role_search_output_sw_model = api.model('RoleSearchOutput', {
    'data': fields.List(fields.Nested(role_sw_model)),
    'records_total': fields.Integer,
    'records_filtered': fields.Integer,
})
