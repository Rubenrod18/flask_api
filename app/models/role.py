import logging
from datetime import datetime

from flask_security import RoleMixin
from peewee import CharField, TimestampField, TextField

from .base import Base as BaseModel

logger = logging.getLogger(__name__)


class Role(BaseModel, RoleMixin):
    class Meta:
        table_name = 'roles'

    name = CharField(unique=True)
    description = TextField(null=True)
    label = CharField()
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)

    def serialize(self, ignore_fields: list = None) -> dict:
        if ignore_fields is None:
            ignore_fields = []

        data = self.__dict__.get('__data__')
        logger.debug(data)

        deleted_at = data.get('deleted_at')

        if isinstance(deleted_at, datetime):
            deleted_at = deleted_at.strftime('%Y-%m-%d %H:%M:%S')

        data = {
            'id': data.get('id'),
            'name': data.get('name'),
            'description': data.get('description'),
            'label': data.get('label'),
            'created_at': data.get('created_at').strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': data.get('updated_at').strftime('%Y-%m-%d %H:%M:%S'),
            'deleted_at': deleted_at,
        }

        if ignore_fields:
            pass

        return data
