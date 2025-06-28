from flask_restx import fields

from app.extensions import api
from app.models.document import StorageType
from app.swagger.core import creator_sw_model, record_monitoring_sw_model

document_sw_model = api.clone(
    'Document',
    record_monitoring_sw_model,
    {
        'created_by': fields.Nested(creator_sw_model),
        'name': fields.String(description='Document name with file extension.', example='document.pdf'),
        'mime_type': fields.String(readonly=True, example='application/pdf'),
        'size': fields.Integer(readonly=True, description='File size in bytes.', example=6000000),
        'url': fields.String(readonly=True, description='URL for getting the document content.'),
        'storage_type': fields.String(enum=StorageType.to_list(), example='local'),
    },
)

document_search_output_sw_model = api.model(
    'DocumentSearch',
    {
        'data': fields.List(fields.Nested(document_sw_model)),
        'records_total': fields.Integer,
        'records_filtered': fields.Integer,
    },
)
