import logging
import time
from datetime import datetime, date, timedelta
from random import randint
from typing import Type, TypeVar

from peewee import CharField, IntegerField, DateField, TimestampField

from . import fake
from app.utils import difference_in_years
from ..extensions import db_wrapper as db

logger = logging.getLogger(__name__)

U = TypeVar('U', bound='User')


class User(db.Model):
    class Meta:
        table_name = 'users'

    name = CharField()
    last_name = CharField()
    age = IntegerField()
    birth_date = DateField()
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)

    def save(self, *args: list, **kwargs: dict) -> int:
        current_date = datetime.utcnow()

        if self.id is None:
            self.created_at = current_date

        if self.deleted_at is None:
            self.updated_at = current_date

        return super(User, self).save(*args, **kwargs)

    def serialize(self: Type[U], ignore_fields: list = None) -> dict:
        if ignore_fields is None:
            ignore_fields = []

        data = self.__dict__.get('__data__')
        logger.debug(data)

        birth_date = data.get('birth_date')
        deleted_at = data.get('deleted_at')

        if isinstance(deleted_at, datetime):
            deleted_at = time.mktime(deleted_at.timetuple())

        if isinstance(birth_date, date):
            birth_date = birth_date.strftime('%Y-%m-%d')

        data = {
            'id': data.get('id'),
            'name': data.get('name'),
            'last_name': data.get('last_name'),
            'age': data.get('age'),
            'birth_date': birth_date,
            'created_at': time.mktime(data.get('created_at').timetuple()),
            'updated_at': time.mktime(data.get('updated_at').timetuple()),
            'deleted_at': deleted_at,
        }

        if ignore_fields:
            pass

        return data

    @classmethod
    def get_fields(self: Type[U], ignore_fields: list = None) -> set:
        if ignore_fields is None:
            ignore_fields = []

        return set(
            filter(
                lambda x: x not in ignore_fields,
                list(self._meta.fields)
            )
        )

    @classmethod
    def fake(self) -> U:
        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.utcnow()

        created_at = datetime.utcnow()
        updated_at = created_at
        deleted_at = None

        if randint(0, 1):
            deleted_at = created_at + timedelta(days=randint(1, 7), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 7), minutes=randint(0, 60))

        age = difference_in_years(birth_date, current_date)

        return User(
            name=fake.name(),
            last_name=fake.last_name(),
            age=age,
            birth_date=birth_date.strftime('%Y-%m-%d'),
            created_at=datetime.utcnow(),
            updated_at=updated_at,
            deleted_at=deleted_at
        )

    @classmethod
    def seed(cls: Type[U]) -> None:
        user = User.fake()
        user.save()

        db.database.commit()
        db.database.close()
