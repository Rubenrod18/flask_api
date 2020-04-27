import logging
import time
from datetime import datetime, timedelta
from random import randint
from typing import TypeVar

from peewee import CharField, TimestampField

from . import fake
from .base import BaseModel
from ..extensions import db_wrapper as db

logger = logging.getLogger(__name__)

R = TypeVar('R', bound='Role')

class Role(BaseModel):
    class Meta:
        table_name = 'roles'

    name = CharField()
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
            'slug': data.get('slug'),
            'created_at': data.get('created_at').strftime('%Y-%m-%d %H:%m:%S'),
            'updated_at': data.get('updated_at').strftime('%Y-%m-%d %H:%m:%S'),
            'deleted_at': deleted_at,
        }

        if ignore_fields:
            pass

        return data

    @classmethod
    def fake(self) -> R:
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(1, 100), minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1):
            deleted_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))

        return Role(
            name=fake.word(),
            slug=fake.slug(),
            created_at=created_at,
            updated_at=updated_at,
            deleted_at=deleted_at
        )

    @classmethod
    def seed(self) -> None:
        role = Role.fake()
        role.save()

        db.database.commit()
        db.database.close()