import mimetypes
import uuid
from datetime import timedelta, datetime
from random import randint
from shutil import copyfile

from flask import current_app
from peewee import fn

from app.models import Document as DocumentModel, User as UserModel
from app.utils import ignore_keys
from app.utils.constants import PDF_MIME_TYPE
from database import fake


class _DocumentFactory:
    @staticmethod
    def _fill(params: dict, exclude: list) -> dict:
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(31, 100),
                                              minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1) and 'deleted_at' not in params:
            deleted_at = created_at + timedelta(days=randint(1, 30),
                                                minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30),
                                                minutes=randint(0, 60))

        created_by = (UserModel.select()
                      .order_by(fn.Random())
                      .limit(1)
                      .get()
                      .id)

        mime_type = fake.random_element([
            PDF_MIME_TYPE,
            # TODO: add more MIME types
        ])
        file_extension = mimetypes.guess_extension(mime_type).replace('.', '')
        internal_filename = '%s.%s' % (uuid.uuid1().hex, file_extension)

        pdf_file = '%s/example.pdf' % current_app.config.get('MOCKUP_DIRECTORY')
        abs_file = '%s/%s' % (current_app.config.get('STORAGE_DIRECTORY'),
                              internal_filename)
        copyfile(pdf_file, abs_file)

        data = {
            'created_by': params.get('created_by') or created_by,
            'name': params.get('name') or fake.file_name(category='office',
                                                         extension=file_extension),
            'internal_filename': params.get('internal_filename') or internal_filename,
            'mime_type': params.get('mime_type') or mime_type,
            'directory_path': current_app.config.get('STORAGE_DIRECTORY'),
            # Between 2MB to 10MB
            'size': params.get('size', fake.random_int(2000000, 10000000)),
            'created_at': created_at,
            'updated_at': updated_at,
            'deleted_at': deleted_at,
        }

        return ignore_keys(data, exclude)

    def make(self, params: dict, to_dict: bool, exclude: list) -> DocumentModel:
        data = self._fill(params, exclude)

        if to_dict:
            document = data
        else:
            model_data = {
                item: data.get(item)
                for item in DocumentModel.get_fields(exclude)
            }
            document = DocumentModel(**model_data)

        return document

    def create(self, params: dict) -> DocumentModel:
        data = self._fill(params, exclude=[])
        return DocumentModel.create(**data)

    def bulk_create(self, total: int, params: dict) -> bool:
        data = []

        for item in range(total):
            data.append(self.make(params, to_dict=False, exclude=[]))

        DocumentModel.bulk_create(data)
        return True
