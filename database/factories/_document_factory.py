import uuid
from datetime import timedelta, datetime
from random import randint

from flask import current_app
from peewee import fn

from app.models.document import Document as DocumentModel
from app.models.user import User as UserModel
from app.utils import ignore_keys
from database import fake


class _DocumentFactory():
    def _fill(self, params: dict, exclude: list) -> dict:
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(31, 100), minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1) and 'deleted_at' not in params:
            deleted_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))

        created_by = (UserModel.select()
                      .order_by(fn.Random())
                      .limit(1)
                      .get()
                      .id)

        file_extension = fake.random_element(['xlsx', 'pdf'])
        mime_types = {
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
        }

        internal_name = '%s.%s' % (uuid.uuid1().hex, file_extension)

        data = {
            'created_by': params.get('created_by') or created_by,
            'name': params.get('name') or fake.file_name(category='office', extension=file_extension),
            'internal_name': params.get('internal_name') or internal_name,
            'mime_type': params.get('mime_type') or mime_types.get(file_extension),
            'filepath': current_app.config.get('STORAGE_DIRECTORY'),
            'size': params.get('size', fake.random_int(2000000, 10000000)), # Between 2MB to 10MB
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
            document = DocumentModel()
            document.created_by = data.get('created_by')
            document.name = data.get('name')
            document.internal_name = data.get('internal_name')
            document.mime_type = data.get('mime_type')
            document.filepath = data.get('filepath')
            document.size = data.get('size')
            document.created_at = data.get('created_at')
            document.update_at = data.get('updated_at')
            document.deleted_at = data.get('deleted_at')

        return document

    def create(self, params: dict) -> DocumentModel:
        exclude = []

        data = self._fill(params, exclude)

        return DocumentModel.create(**data)

    def bulk_create(self, total: int, params: dict) -> None:
        data = []

        for item in range(total):
            data.append(self.make(params, False, []))

        DocumentModel.bulk_create(data)
