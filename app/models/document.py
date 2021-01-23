import logging

from flask import url_for
from peewee import CharField, ForeignKeyField, TimestampField, IntegerField

from app.models.base import Base as BaseModel
from app.models.user import User as UserModel

logger = logging.getLogger(__name__)


class Document(BaseModel):
    class Meta:
        table_name = 'documents'

    created_by = ForeignKeyField(UserModel, column_name='created_by')
    name = CharField()
    internal_filename = CharField(unique=True)
    mime_type = CharField()
    directory_path = CharField()
    size = IntegerField()
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)

    @property
    def url(self):
        return url_for('documents_document_resource', document_id=self.id,
                       _external=True)

    def get_filepath(self):
        return '%s/%s' % (self.directory_path, self.internal_filename)
