import sqlalchemy as sa
from flask import url_for
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.user import User
from app.utils.constants import BaseEnum


class StorageType(BaseEnum):
    LOCAL = 'local'
    GDRIVE = 'gdrive'

    def __str__(self):
        return self.value


class Document(Base):
    __tablename__ = 'documents'

    created_by = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=True)
    created_by_user = relationship(User, backref='documents')

    name = sa.Column(sa.String(255), nullable=False)
    mime_type = sa.Column(sa.String(255), nullable=False)
    size = sa.Column(sa.Integer, nullable=False)

    storage_type = sa.Column(sa.Enum(StorageType), nullable=False, default=StorageType.LOCAL)
    storage_id = sa.Column(sa.String(255), nullable=True)

    # Local-only fields (still used if storage_type == LOCAL)
    internal_filename = sa.Column(sa.String(255), nullable=True, unique=True)
    directory_path = sa.Column(sa.String(255), nullable=True)

    @property
    def url(self) -> str | None:
        if self.storage_type == StorageType.LOCAL:
            return url_for('documents_document_resource', document_id=self.id, _external=True)
        elif self.storage_type == StorageType.GDRIVE:
            return f'https://drive.google.com/file/d/{self.storage_id}/view'
        return None

    def get_filepath(self) -> str | None:
        if self.storage_type == StorageType.LOCAL:
            return f'{self.directory_path}/{self.internal_filename}'
        return None
