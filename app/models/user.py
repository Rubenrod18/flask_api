import logging
import os
import time
from datetime import datetime, date, timedelta
from random import randint
from typing import TypeVar

from flask_security import UserMixin, PeeweeUserDatastore, hash_password
from peewee import CharField, DateField, TimestampField, ForeignKeyField, fn, BooleanField

from . import fake
from .base import BaseModel as BaseModel
from .role import Role as RoleModel, Role
from ..extensions import db_wrapper as db

logger = logging.getLogger(__name__)

U = TypeVar('U', bound='User')


class User(BaseModel, UserMixin):
    class Meta:
        table_name = 'users'

    role = ForeignKeyField(RoleModel, backref='roles')
    name = CharField()
    last_name = CharField()
    email = CharField(null=False, unique=True)
    password = CharField(null=False)
    birth_date = DateField()
    active = BooleanField(default=True)
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)

    def save(self, *args: list, **kwargs: dict) -> int:
        current_date = datetime.utcnow()

        if self.id is None and self.created_at is None:
            self.created_at = current_date

        if self.deleted_at is None:
            self.updated_at = current_date

        if self.password:
            self.password = hash_password(self.password)

        return super(User, self).save(*args, **kwargs)

    def serialize(self, ignore_fields: list = None) -> dict:
        if ignore_fields is None:
            ignore_fields = []

        data = self.__dict__.get('__data__')
        logger.debug(data)

        birth_date = data.get('birth_date')
        deleted_at = data.get('deleted_at')
        active = 1 if data.get('active') else 0

        if isinstance(deleted_at, datetime):
            deleted_at = deleted_at.strftime('%Y-%m-%d %H:%m:%S')

        if isinstance(birth_date, date):
            birth_date = birth_date.strftime('%Y-%m-%d')

        data = {
            'id': data.get('id'),
            'name': data.get('name'),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'birth_date': birth_date,
            'active': active,
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
    def fake(self, data: dict = None) -> U:
        if data is None:
            data = {}

        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(1, 100), minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1) and 'deleted_at' not in data:
            deleted_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))

        role = (RoleModel.select()
                .where(RoleModel.deleted_at.is_null())
                .order_by(fn.Random())
                .get())

        user = User()
        user.role = data.get('role') if data.get('role') else role
        user.name = data.get('name') if data.get('name') else fake.name()
        user.last_name = data.get('last_name') if data.get('last_name') else fake.last_name()
        user.email = data.get('email') if data.get('email') else fake.email()
        user.password = data.get('password') if data.get('password') else '123456'
        user.birth_date = data.get('birth_date') if data.get('birth_date') else birth_date.strftime('%Y-%m-%d')
        user.active = data.get('active') if data.get('active') else fake.boolean()
        user.created_at = created_at
        user.updated_at = updated_at
        user.deleted_at = deleted_at

        return user

    @classmethod
    def seed(self) -> None:
        with db.database.atomic():
            for i in range(10):
                user = self.fake()
                user.save()

            user = self.fake({
                'email': os.environ.get('TEST_USER_EMAIL'),
                'password': os.environ.get('TEST_USER_PASSWORD'),
                'deleted_at': None,
                'active': True,
            })
            user.save()

        db.database.close()


user_datastore = PeeweeUserDatastore(db, User, Role, None)
