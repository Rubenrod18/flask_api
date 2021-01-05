from flask_restx import fields

from app.extensions import api
from app.swagger.core import record_monitoring_sw_model

role_input_sw_model = api.model('RoleInput', {
    'description': fields.String,
    'label': fields.String(required=True),
})

role_sw_model = api.clone('Role', record_monitoring_sw_model, {
    'name': fields.String(readonly=True),
    'description': fields.String,
    'label': fields.String,
})

role_search_output_sw_model = api.model('RoleSearchOutput', {
    'data': fields.List(fields.Nested(role_sw_model)),
    'records_total': fields.Integer,
    'records_filtered': fields.Integer,
})
