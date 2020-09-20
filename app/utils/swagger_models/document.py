from flask_restx import fields

from app.extensions import api
from app.utils.swagger_models import CREATOR_SW_MODEL


DOCUMENT_SW_MODEL = api.model('Document', {
    'id': fields.Integer(),
    'name': fields.String,
    'internal_name': fields.String,
    'mime_type': fields.String,
    'size': fields.Integer,
    'url': fields.String,
    'created_at': fields.String(),
    'updated_at': fields.String(),
    'deleted_at': fields.String(),
    'created_by': fields.Nested(CREATOR_SW_MODEL),
})

DOCUMENT_OUTPUT_SW_MODEL = api.model('DocumentOutput', {
    'data': fields.Nested(DOCUMENT_SW_MODEL),
})

DOCUMENT_SEARCH_OUTPUT_SW_MODEL = api.model('DocumentSearch', {
    'data': fields.List(fields.Nested(DOCUMENT_SW_MODEL)),
    'records_total': fields.Integer,
    'records_filtered': fields.Integer,
})
