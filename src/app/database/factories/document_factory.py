import shutil
import uuid

import factory
from flask import current_app
from sqlalchemy import func

from app.database.factories.base_factory import BaseFactory, faker
from app.extensions import db
from app.managers import UserManager
from app.models import Document, User
from app.utils.constants import PDF_MIME_TYPE

_user_manager = UserManager()


class DocumentFactory(BaseFactory):
    class Meta:
        model = Document

    name = factory.Sequence(lambda n: f'document_name_{n}')
    size = faker.random_int(2_000_000, 10_000_000)

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
    def mime_type(self):
        return faker.random_element([PDF_MIME_TYPE])

    @factory.lazy_attribute
    def created_by_user(self):
        return db.session.query(User).filter(User.deleted_at.is_(None)).order_by(func.random()).limit(1).first()
