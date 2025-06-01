import logging
import mimetypes
import uuid

from flask import current_app, Response, send_file
from flask_login import current_user
from werkzeug.exceptions import InternalServerError

from app.extensions import db
from app.file_storages import LocalStorage
from app.managers import DocumentManager
from app.models import Document
from app.services.base import BaseService

logger = logging.getLogger(__name__)


class DocumentService(BaseService):
    def __init__(self, file_storage: LocalStorage = None):
        super().__init__(manager=DocumentManager())
        self.file_storage = file_storage or LocalStorage()

    def create(self, **kwargs) -> Document:
        file_extension = mimetypes.guess_extension(kwargs.get('mime_type'))
        internal_filename = f'{uuid.uuid1().hex}{file_extension}'
        filepath = f'{current_app.config.get("STORAGE_DIRECTORY")}/{internal_filename}'

        try:
            self.file_storage.save_bytes(kwargs.get('file_data'), filepath)

            data = {
                'created_by': current_user.id,
                'name': kwargs.get('filename'),
                'internal_filename': internal_filename,
                'mime_type': kwargs.get('mime_type'),
                'directory_path': current_app.config.get('STORAGE_DIRECTORY'),
                'size': self.file_storage.get_filesize(filepath),
            }
            document = self.manager.create(**data)
            db.session.add(document)
            db.session.flush()
        except Exception as e:
            self.file_storage.delete_file(filepath)
            logger.debug(e)
            raise InternalServerError() from e
        else:
            return document

    def find_by_id(self, record_id: int, *args) -> Document | None:
        return self.manager.find_by_id(record_id, *args)

    def get(self, **kwargs) -> dict:
        return self.manager.get(**kwargs)

    def save(self, record_id: int, **kwargs) -> Document:
        document = self.manager.find_by_id(record_id)
        # QUESTION: The app doesn't have file versioning, should we consider this feature in the future?
        filepath = f'{document.directory_path}/{document.internal_filename}'

        try:
            self.file_storage.save_bytes(kwargs.get('file_data'), filepath, override=True)

            data = {
                'name': kwargs.get('filename'),
                'mime_type': kwargs.get('mime_type'),
                'size': self.file_storage.get_filesize(filepath),
            }
            document = self.manager.save(record_id, **data)
            db.session.add(document)
            db.session.flush()
        except Exception as e:  # HACK: Add the proper exceptions here
            self.file_storage.delete_file(filepath)
            logger.debug(e)
            raise InternalServerError() from e
        else:
            return document.reload()

    def delete(self, record_id: int) -> Document:
        return self.manager.delete(record_id)

    def get_document_content(self, document_id: int, request_args: dict) -> Response:
        as_attachment = request_args.get('as_attachment', 0)
        document = self.manager.find_by_id(document_id)

        mime_type = document.mime_type
        file_extension = mimetypes.guess_extension(mime_type)

        kwargs = {
            'path_or_file': document.get_filepath(),
            'mimetype': mime_type,
            'as_attachment': as_attachment,
        }

        if as_attachment:
            kwargs['download_name'] = (
                document.name if document.name.find(file_extension) else f'{document.name}{file_extension}'
            )

        return send_file(**kwargs)
