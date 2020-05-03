import logging
from datetime import datetime
from typing import TypeVar

from flask_security import RoleMixin
from peewee import CharField, TimestampField, TextField

from .base import BaseModel

logger = logging.getLogger(__name__)

R = TypeVar('R', bound='Role')


class Role(BaseModel, RoleMixin):
    class Meta:
        table_name = 'roles'

    name = CharField()
    description = TextField(null=True)
    slug = CharField(unique=True)
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
            deleted_at = deleted_at.strftime('%Y-%m-%d %H:%m:%S')

        data = {
            'id': data.get('id'),
            'name': data.get('name'),
            'description': data.get('description'),
            'slug': data.get('slug'),
            'created_at': data.get('created_at').strftime('%Y-%m-%d %H:%m:%S'),
            'updated_at': data.get('updated_at').strftime('%Y-%m-%d %H:%m:%S'),
            'deleted_at': deleted_at,
        }

        if ignore_fields:
            pass

        return data
