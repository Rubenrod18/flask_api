from flask_restx import fields

from app.extensions import api
from app.swagger.core import creator_sw_model

document_sw_model = api.model('Document', {
    'id': fields.Integer(),
    'name': fields.String,
    'mime_type': fields.String,
    'size': fields.Integer,
    'url': fields.String,
    'created_at': fields.String(),
    'updated_at': fields.String(),
    'deleted_at': fields.String(),
    'created_by': fields.Nested(creator_sw_model),
})

document_output_sw_model = api.model('DocumentOutput', {
    'data': fields.Nested(document_sw_model),
})

document_search_output_sw_model = api.model('DocumentSearch', {
    'data': fields.List(fields.Nested(document_sw_model)),
    'records_total': fields.Integer,
    'records_filtered': fields.Integer,
})
