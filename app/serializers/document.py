import magic
from flask import url_for
from marshmallow import fields, validate, pre_load, post_dump
from werkzeug.exceptions import UnprocessableEntity

from app.extensions import ma
from app.serializers.core import TimestampField
from config import Config


class DocumentSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id', 'name', 'mime_type', 'size', 'url', 'created_at',
            'updated_at', 'deleted_at', 'created_by', 'internal_filename'
        )

    id = fields.Int()
    created_by = fields.Nested('UserSchema', only=('id', 'name', 'last_name',
                                                   'email'))
    name = fields.Str()
    internal_filename = fields.Str()
    mime_type = fields.Str()
    directory_path = fields.Str()
    size = fields.Integer()
    created_at = TimestampField()
    updated_at = TimestampField()
    deleted_at = TimestampField()

    @post_dump()
    def make_url(self, data, **kwargs):
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


class GetDocumentDataInputSchema(ma.Schema):
    as_attachment = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def convert_to_integer(self, value, many, **kwargs):
        if 'as_attachment' in value:
            value['as_attachment'] = int(value.get('as_attachment'))
        return value
