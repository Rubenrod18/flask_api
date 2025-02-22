import logging
import mimetypes
import uuid
from abc import ABC

from flask import current_app, Response, send_file
from flask_login import current_user
from marshmallow import EXCLUDE
from werkzeug.exceptions import InternalServerError

from app.extensions import db
from app.helpers.file_storage.local_storage import LocalStorage
from app.helpers.request_helpers import get_request_file
from app.managers import DocumentManager
from app.models import Document
from app.serializers import DocumentAttachmentSerializer, DocumentSerializer, SearchSerializer
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class DocumentService(BaseService, ABC):
    def __init__(self, file_storage: LocalStorage = None):
        super().__init__(
            manager=DocumentManager(), serializer=DocumentSerializer(), search_serializer=SearchSerializer()
        )
        self.file_storage = file_storage or LocalStorage()

    def create(self, **kwargs) -> Document:
        data = self.serializer.valid_request_file(kwargs)

        file_extension = mimetypes.guess_extension(data.get('mime_type'))
        internal_filename = f'{uuid.uuid1().hex}{file_extension}'
        filepath = f'{current_app.config.get("STORAGE_DIRECTORY")}/{internal_filename}'

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
            db.session.add(document)
            db.session.flush()
        except Exception as e:
            self.file_storage.delete_file(filepath)
            logger.debug(e)
            raise InternalServerError()
        else:
            return document

    def find(self, document_id: int, *args) -> Document | None:
        self.serializer.load({'id': document_id}, partial=True)
        return self.manager.find(document_id, *args)

    def get(self, **kwargs) -> dict:
        data = self.search_serializer.load(kwargs)
        return self.manager.get(**data)

    def save(self, document_id: int, **kwargs) -> Document:
        self.serializer.load({'id': document_id}, partial=True)
        file = get_request_file()
        data = self.serializer.valid_request_file(file)

        document = self.manager.find(document_id)
        filepath = f'{document.directory_path}/{document.internal_filename}'

        try:
            self.file_storage.save_bytes(data.get('file_data'), filepath, override=True)

            data = {
                'name': data.get('filename'),
                'mime_type': data.get('mime_type'),
                'size': self.file_storage.get_filesize(filepath),
            }
            document = self.manager.save(document_id, **data)
            db.session.add(document)
            db.session.flush()
        except Exception as e:
            self.file_storage.delete_file(filepath)
            logger.debug(e)
            raise InternalServerError()
        else:
            return document.reload()

    def delete(self, document_id: int) -> Document:
        self.serializer.load({'id': document_id}, partial=True)
        return self.manager.delete(document_id)

    def get_document_content(self, document_id: int, **kwargs) -> Response:
        self.serializer.load({'id': document_id}, partial=True)
        request_args = DocumentAttachmentSerializer().load(kwargs, unknown=EXCLUDE)

        as_attachment = request_args.get('as_attachment', 0)
        document = self.manager.find(document_id)

        mime_type = document.mime_type
        file_extension = mimetypes.guess_extension(mime_type)

        attachment_filename = (
            document.name if document.name.find(file_extension) else f'{document.name}{file_extension}'
        )

        kwargs = {
            'path_or_file': document.get_filepath(),
            'mimetype': mime_type,
            'as_attachment': as_attachment,
        }

        if as_attachment:
            kwargs['attachment_filename'] = attachment_filename
        return send_file(**kwargs)
