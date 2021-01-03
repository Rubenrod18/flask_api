import logging

import magic
from flask import url_for
from marshmallow import fields, validate, pre_load, post_dump, validates
from werkzeug.exceptions import UnprocessableEntity, NotFound

from app.extensions import ma
from app.managers import DocumentManager
from app.serializers.core import TimestampField
from config import Config

logger = logging.getLogger(__name__)
document_manager = DocumentManager()


class DocumentSerializer(ma.Schema):
    class Meta:
        ordered = True

    id = fields.Int()
    created_by = fields.Nested('UserSerializer', only=('id', 'name', 'last_name',
                                                       'email'))
    name = fields.Str()
    internal_filename = fields.Str()
    mime_type = fields.Str()
    directory_path = fields.Str(load_only=True)
    size = fields.Integer()
    created_at = TimestampField(dump_only=True)
    updated_at = TimestampField(dump_only=True)
    deleted_at = TimestampField(dump_only=True)

    @validates('id')
    def validate_id(self, document_id):
        args = (document_manager.model.deleted_at.is_null(),)
        document = document_manager.find(document_id, *args)

        if document is None:
            logger.debug(f'Document "{document_id}" not found.')
            raise NotFound('Document not found')

        if document.deleted_at is not None:
            logger.debug(f'Document "{document_id}" already deleted.')
            raise NotFound('Document not found')

    @post_dump()
    def wrap(self, data, **kwargs):
        data['url'] = url_for('documents_document_resource',
                              document_id=data['id'],
                              _external=True)
        return data

    @staticmethod
    def valid_request_file(data):
        is_valid_mime_type = (data.get('mime_type') in Config.ALLOWED_MIME_TYPES)

        file_content_type = magic.from_buffer(data.get('file_data'), mime=True)
        is_valid_file_content_type = (file_content_type in Config.ALLOWED_MIME_TYPES)

        if not is_valid_mime_type or not is_valid_file_content_type:
            raise UnprocessableEntity('mime_type not valid')

        return data


class DocumentAttachmentSerializer(ma.Schema):
    as_attachment = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def process_input(self, value, many, **kwargs):
        if 'as_attachment' in value:
            value['as_attachment'] = int(value.get('as_attachment'))
        return value
