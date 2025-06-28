import random
import shutil
import uuid

import factory
from flask import current_app
from sqlalchemy import func

from app.database.factories.base_factory import BaseFactory
from app.extensions import db
from app.models import Document, User
from app.models.document import StorageType
from app.utils.constants import PDF_MIME_TYPE


class DocumentFactory(BaseFactory):
    class Meta:
        model = Document

    name = factory.Sequence(lambda n: f'document_name_{n}')
    size = factory.Faker('random_int', min=2_000_000, max=10_000_000)
    mime_type = factory.Faker('random_element', elements=[PDF_MIME_TYPE])
    storage_type = factory.Iterator(StorageType.to_list())
    storage_id = random.choice([uuid.uuid4().hex, None])
    created_at = factory.Faker('date_time_between', start_date='-3y', end_date='now')
    deleted_at = random.choice([factory.Faker('date_time_between', start_date='-1y', end_date='now'), None])

    @factory.lazy_attribute
    def directory_path(self):
        return current_app.config.get('STORAGE_DIRECTORY')

    @factory.lazy_attribute
    def internal_filename(self):
        filename = f'{uuid.uuid1().hex}.pdf'
        shutil.copy(
            src=f'{current_app.config.get("MOCKUP_DIRECTORY")}/example.pdf',
            dst=f'{current_app.config.get("STORAGE_DIRECTORY")}/{filename}',
        )
        return filename

    @factory.lazy_attribute
    def created_by_user(self):
        return (
            db.session.query(User)
            .filter(User.deleted_at.is_(None))
            .order_by(func.random())  # pylint: disable=not-callable
            .limit(1)
            .first()
        )

    @factory.lazy_attribute
    def updated_at(self):
        if self.deleted_at:
            updated_at = self.deleted_at
        else:
            # NOTE: This case always applies on the creation
            updated_at = self.created_at
        return updated_at


class LocalDocumentFactory(DocumentFactory):
    storage_type = StorageType.LOCAL.value
    storage_id = None


class GDriveDocumentFactory(DocumentFactory):
    storage_type = StorageType.GDRIVE.value
    storage_id = uuid.uuid4().hex

    @factory.lazy_attribute
    def directory_path(self):
        return None

    @factory.lazy_attribute
    def internal_filename(self):
        return None
