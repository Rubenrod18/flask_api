import logging
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

    @classmethod
    def fake(self) -> R:
        created_at = datetime.utcnow()
        updated_at = created_at
        deleted_at = None

        if randint(0, 1):
            deleted_at = created_at + timedelta(days=randint(1, 7), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 7), minutes=randint(0, 60))

        return Role(
            name=fake.word(),
            slug=fake.slug(),
            created_at=datetime.utcnow(),
            updated_at=updated_at,
            deleted_at=deleted_at
        )

    @classmethod
    def seed(self) -> None:
        role = Role.fake()
        role.save()

        db.database.commit()
        db.database.close()