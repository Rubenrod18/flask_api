import logging
from datetime import datetime

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

    @property
    def url(self):
        return url_for('documents.documentresource', document_id=self.id, _external=True)

    def get_filepath(self):
        return '%s/%s' % (self.directory_path, self.internal_filename)

    def serialize(self, ignore_fields: list = None) -> dict:
        ignore_fields = ignore_fields or []

        data = self.__dict__.get('__data__')
        logger.debug(data)

        deleted_at = data.get('deleted_at')

        if isinstance(deleted_at, datetime):
            deleted_at = deleted_at.strftime('%Y-%m-%d %H:%M:%S')

        data = {
            'id': data.get('id'),
            'name': data.get('name'),
            'mime_type': data.get('mime_type'),
            'size': data.get('size'),
            'url': self.url,
            'created_at': data.get('created_at').strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': data.get('updated_at').strftime('%Y-%m-%d %H:%M:%S'),
            'deleted_at': deleted_at,
            'created_by': data.get('created_by'),
        }

        if ignore_fields:
            pass

        return data
