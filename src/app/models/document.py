import logging

from flask import url_for
from sqlalchemy.orm import relationship

from app.models.base import Base as BaseModel
from app.models.user import User as UserModel
import sqlalchemy as sa

logger = logging.getLogger(__name__)


class Document(BaseModel):
    __tablename__ = 'documents'

    created_by = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=True)
    created_by_user = relationship(UserModel, backref='documents')

    name = sa.Column(sa.String(255), nullable=False)
    internal_filename = sa.Column(sa.String(255), nullable=False, unique=True)
    mime_type = sa.Column(sa.String(255), nullable=False)
    directory_path = sa.Column(sa.String(255), nullable=False)
    size = sa.Column(sa.Integer, nullable=False)

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)

    @property
    def url(self):
        return url_for('documents_document_resource', document_id=self.id,
                       _external=True)

    def get_filepath(self):
        return '%s/%s' % (self.directory_path, self.internal_filename)
