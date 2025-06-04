import magic
from flask import url_for
from marshmallow import fields, post_dump, pre_load, validate, validates
from werkzeug.exceptions import NotFound, UnprocessableEntity

from app.extensions import ma
from app.models import Document
from app.repositories import DocumentRepository
from app.serializers.core import RepositoryMixin
from config import Config


class DocumentSerializer(ma.SQLAlchemySchema, RepositoryMixin):
    class Meta:
        model = Document
        ordered = True

    repository_classes = {'document_repository': DocumentRepository}

    id = ma.auto_field()
    name = ma.auto_field()
    internal_filename = ma.auto_field()
    mime_type = ma.auto_field()
    size = ma.auto_field()

    directory_path = ma.auto_field(load_only=True)

    created_by_user = fields.Nested('UserSerializer', only=('id', 'name', 'last_name', 'email'), dump_only=True)
    created_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    deleted_at = ma.auto_field(dump_only=True, format='%Y-%m-%d %H:%M:%S')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._document_repository = self.get_repository('document_repository')

    @validates('id')
    def validate_id(self, document_id):
        args = (self._document_repository.model.deleted_at.is_(None),)
        document = self._document_repository.find_by_id(document_id, *args)

        if document is None or document.deleted_at is not None:
            raise NotFound('Document not found')

    @post_dump()
    def wrap(self, data, **kwargs):  # pylint: disable=unused-argument
        data['url'] = url_for('documents_document_resource', document_id=data['id'], _external=True)
        data['created_by'] = data.pop('created_by_user')
        return data

    @staticmethod
    def valid_request_file(data):
        if not data.get('file_data'):
            raise UnprocessableEntity('empty file')

        is_valid_mime_type = data.get('mime_type') in Config.ALLOWED_MIME_TYPES

        file_content_type = magic.from_buffer(data.get('file_data'), mime=True)
        is_valid_file_content_type = file_content_type in Config.ALLOWED_MIME_TYPES

        if not is_valid_mime_type or not is_valid_file_content_type:
            raise UnprocessableEntity('mime_type not valid')

        return data


class DocumentAttachmentSerializer(ma.Schema):
    as_attachment = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def process_input(self, value, many, **kwargs):  # pylint: disable=unused-argument
        if 'as_attachment' in value:
            value['as_attachment'] = int(value.get('as_attachment'))
        return value
