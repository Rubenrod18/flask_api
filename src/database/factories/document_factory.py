import mimetypes
import uuid

import factory
from flask import current_app
from sqlalchemy import func

from app.extensions import db
from app.managers import UserManager
from app.models import Document as DocumentModel, User as UserModel
from app.utils.constants import PDF_MIME_TYPE
from database import fake
from database.factories.base_factory import BaseFactory


_user_manager = UserManager()


class DocumentFactory(BaseFactory):
    class Meta:
        model = DocumentModel

    name = factory.Sequence(lambda n: f'document_name_{n}')
    size = fake.random_int(2_000_000, 10_000_000)

    @factory.lazy_attribute
    def directory_path(self):
        return current_app.config.get('STORAGE_DIRECTORY')

    @factory.lazy_attribute
    def internal_filename(self):
        return '%s.%s' % (uuid.uuid1().hex, self.mime_type)

    @factory.lazy_attribute
    def mime_type(self):
        mime_type = fake.random_element([PDF_MIME_TYPE])
        return mimetypes.guess_extension(mime_type).replace('.', '')

    @factory.lazy_attribute
    def created_by_user(self):
        return (
            db.session.query(UserModel)
            .filter(UserModel.deleted_at.is_(None))
            .order_by(func.random())
            .limit(1)
            .first()
        )
