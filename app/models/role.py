import logging

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
