import logging
from datetime import datetime, date
from typing import TypeVar

from flask import current_app
from flask_security import UserMixin, PeeweeUserDatastore, hash_password
from itsdangerous import URLSafeSerializer, TimestampSigner
from peewee import CharField, DateField, TimestampField, ForeignKeyField, BooleanField, FixedCharField

from .base import Base as BaseModel
from .role import Role as RoleModel
from ..extensions import db_wrapper as db

logger = logging.getLogger(__name__)

U = TypeVar('U', bound='User')


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
            self.password = self.ensure_password(self.password)

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

    def get_reset_token(self) -> str:
        secret_key = current_app.config.get('SECRET_KEY')
        expire_in = current_app.config.get('RESET_TOKEN_EXPIRES')
        salt = expire_in.__str__()

        s1 = URLSafeSerializer(secret_key, salt)
        s2 = TimestampSigner(secret_key)

        data = s1.dumps({'user_id': self.id})
        return s2.sign(data).decode('utf-8')

    @classmethod
    def get_fields(cls, ignore_fields: list = None, sort_order: list = None) -> set:
        if ignore_fields is None:
            ignore_fields = []

        if sort_order is None:
            sort_order = []

        fields = set(filter(
            lambda x: x not in ignore_fields,
            list(cls._meta.fields)
        ))

        if sort_order and len(fields) == len(sort_order):
            fields = sorted(fields, key=lambda x: sort_order.index(x))

        return fields

    @staticmethod
    def verify_reset_token(token: str) -> any:
        secret_key = current_app.config.get('SECRET_KEY')
        expire_in = current_app.config.get('RESET_TOKEN_EXPIRES')
        salt = expire_in.__str__()

        s1 = URLSafeSerializer(secret_key, salt)
        s2 = TimestampSigner(secret_key)

        try:
            parsed_token = s2.unsign(token, max_age=expire_in).decode('utf-8')
            user_id = s1.loads(parsed_token)['user_id']
        except:
            return None
        return User.get_or_none(user_id)

    @staticmethod
    def ensure_password(plain_text: str) -> str:
        hashed_password = None

        if plain_text:
            hashed_password = hash_password(plain_text)

        return hashed_password


user_datastore = PeeweeUserDatastore(db, User, RoleModel, None)
