import logging
from datetime import datetime, date

from flask_security import UserMixin, PeeweeUserDatastore, hash_password
from peewee import CharField, DateField, TimestampField, ForeignKeyField, BooleanField, FixedCharField

from .base import BaseModel as BaseModel
from .role import Role as RoleModel, Role
from ..extensions import db_wrapper as db

logger = logging.getLogger(__name__)


class User(BaseModel, UserMixin):
    class Meta:
        table_name = 'users'

    created_by = ForeignKeyField('self', null=True, backref='children', column_name='created_by')
    role = ForeignKeyField(RoleModel, backref='roles')
    name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField(null=False)
    genre = FixedCharField(max_length=1, choices=(('m', 'male',), ('f', 'female')), null=True)
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
            'genre': data.get('genre'),
            'birth_date': birth_date,
            'active': active,
            'created_at': data.get('created_at').strftime('%Y-%m-%d %H:%m:%S'),
            'updated_at': data.get('updated_at').strftime('%Y-%m-%d %H:%m:%S'),
            'deleted_at': deleted_at,
            'created_by': data.get('created_by'),
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


user_datastore = PeeweeUserDatastore(db, User, Role, None)
