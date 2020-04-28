import logging
from datetime import datetime, date, timedelta
from random import randint
from typing import TypeVar

from peewee import CharField, IntegerField, DateField, TimestampField, ForeignKeyField, fn

from . import fake
from app.utils import difference_in_years
from .role import Role as RoleModel
from ..extensions import db_wrapper as db

logger = logging.getLogger(__name__)

U = TypeVar('U', bound='User')


class User(db.Model):
    class Meta:
        table_name = 'users'

    role = ForeignKeyField(RoleModel, backref='roles')
    name = CharField()
    last_name = CharField()
    age = IntegerField()
    birth_date = DateField()
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)

    def save(self, *args: list, **kwargs: dict) -> int:
        current_date = datetime.utcnow()

        if self.id is None and self.created_at is None:
            self.created_at = current_date

        if self.deleted_at is None:
            self.updated_at = current_date

        return super(User, self).save(*args, **kwargs)

    def serialize(self, ignore_fields: list = None) -> dict:
        if ignore_fields is None:
            ignore_fields = []

        data = self.__dict__.get('__data__')
        logger.debug(data)

        birth_date = data.get('birth_date')
        deleted_at = data.get('deleted_at')

        if isinstance(deleted_at, datetime):
            deleted_at = deleted_at.strftime('%Y-%m-%d %H:%m:%S')

        if isinstance(birth_date, date):
            birth_date = birth_date.strftime('%Y-%m-%d')

        data = {
            'id': data.get('id'),
            'name': data.get('name'),
            'last_name': data.get('last_name'),
            'age': data.get('age'),
            'birth_date': birth_date,
            'created_at': data.get('created_at').strftime('%Y-%m-%d %H:%m:%S'),
            'updated_at': data.get('updated_at').strftime('%Y-%m-%d %H:%m:%S'),
            'deleted_at': deleted_at,
            'role': self.role.serialize(),
        }

        if ignore_fields:
            match_fields = set(data.keys()) & set(ignore_fields)

            data = {
                k: v
                for (k, v) in data.items()
                if k not in match_fields
            }

        return data

    @classmethod
    def get_fields(self, ignore_fields: list = None, sort_order: list = None) -> set:
        if ignore_fields is None:
            ignore_fields = []

        if sort_order is None:
            sort_order = []

        fields = set(filter(
            lambda x: x not in ignore_fields,
            list(self._meta.fields)
        ))

        if sort_order and len(fields) == len(sort_order):
            fields = sorted(fields, key=lambda x: sort_order.index(x))

        return fields

    @classmethod
    def fake(self) -> U:
        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(1, 100), minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1):
            deleted_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))

        age = difference_in_years(birth_date, current_date)

        role = (RoleModel.select()
               .where(RoleModel.deleted_at.is_null())
               .order_by(fn.Random())
               .get())

        return User(
            role=role,
            name=fake.name(),
            last_name=fake.last_name(),
            age=age,
            birth_date=birth_date.strftime('%Y-%m-%d'),
            created_at=created_at,
            updated_at=updated_at,
            deleted_at=deleted_at
        )

    @classmethod
    def seed(self) -> None:
        user = User.fake()
        user.save()

        db.database.commit()
        db.database.close()
