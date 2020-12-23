import logging
import mimetypes
import os
import uuid

from flask import current_app, send_file
from flask_login import current_user
from marshmallow import ValidationError, EXCLUDE
from werkzeug.exceptions import UnprocessableEntity, InternalServerError, NotFound, BadRequest

from app.managers import DocumentManager
from app.models import Document as DocumentModel
from app.serializers import DocumentSerializer, DocumentAttachmentSerializer
from app.services.base import BaseService
from app.utils import get_request_file
from app.utils.file_storage import FileStorage

logger = logging.getLogger(__name__)


class DocumentService(BaseService):

    def __init__(self):
        super(DocumentService, self).__init__()
        self.manager = DocumentManager()
        self.serializer = DocumentSerializer()
        self.file_storage = FileStorage()

    def create(self, **kwargs):
        try:
            data = self.serializer.valid_request_file(kwargs)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        file_extension = mimetypes.guess_extension(data.get('mime_type'))
        internal_filename = '%s%s' % (uuid.uuid1().hex, file_extension)
        filepath = '%s/%s' % (
            current_app.config.get('STORAGE_DIRECTORY'), internal_filename
        )

        try:
            self.file_storage.save_bytes(data.get('file_data'), filepath)

            data = {
                'created_by': current_user.id,
                'name': data.get('filename'),
                'internal_filename': internal_filename,
                'mime_type': data.get('mime_type'),
                'directory_path': current_app.config.get('STORAGE_DIRECTORY'),
                'size': self.file_storage.get_filesize(filepath),
            }
            document = self.manager.create(**data)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.debug(e)
            raise InternalServerError()
        else:
            return document

    def find(self, document_id: int, *args):
        document = self.manager.find(document_id, *args)
        if document is None:
            raise NotFound('Document doesn\'t exist')
        return document

    def save(self, document_id: int, **kwargs):
        document = self.manager.find(document_id)
        if document is None:
            raise BadRequest('Document doesn\'t exist')

        if document.deleted_at is not None:
            raise BadRequest('Document already deleted')

        try:
            file = get_request_file()
            data = self.serializer.valid_request_file(file)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        filepath = f'{document.directory_path}/{document.internal_filename}'
        try:
            fs = FileStorage()
            fs.save_bytes(data.get('file_data'), filepath, override=True)

            data = {
                'name': data.get('filename'),
                'mime_type': data.get('mime_type'),
                'size': fs.get_filesize(filepath),
            }
            self.manager.save(document_id, **data)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.debug(e)
            raise InternalServerError()

        args = (DocumentModel.deleted_at.is_null(),)
        return self.manager.find(document_id, *args)

    def delete(self, document_id: int):
        document = self.manager.find(document_id)
        if document is None:
            raise NotFound('Document doesn\'t exist')

        if document.deleted_at is not None:
            raise BadRequest('Document already deleted')

        return self.manager.delete(document_id)

    def get_document_content(self, document_id: int, **kwargs):
        args = (DocumentModel.deleted_at.is_null(),)
        document = self.manager.find(document_id, *args)
        if document is None:
            raise NotFound('Document doesn\'t exist')

        try:
            request_args = DocumentAttachmentSerializer().load(kwargs,
                                                               unknown=EXCLUDE)
            as_attachment = request_args.get('as_attachment', 0)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        mime_type = document.mime_type
        file_extension = mimetypes.guess_extension(mime_type)

        attachment_filename = document.name if document.name.find(
            file_extension) else f'{document.name}{file_extension}'

        kwargs = {
            'filename_or_fp': document.get_filepath(),
            'mimetype': mime_type,
            'as_attachment': as_attachment,
        }

        if as_attachment:
            kwargs['attachment_filename'] = attachment_filename
        return send_file(**kwargs)
