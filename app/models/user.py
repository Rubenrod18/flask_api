import logging
from datetime import datetime, date

from flask import current_app
from flask_security import UserMixin, PeeweeUserDatastore, hash_password
from flask_security.utils import verify_hash
from itsdangerous import URLSafeSerializer, TimestampSigner
from peewee import CharField, DateField, TimestampField, ForeignKeyField, BooleanField, FixedCharField, ManyToManyField

from .base import Base as BaseModel
from .role import Role as RoleModel
from ..extensions import db_wrapper as db

logger = logging.getLogger(__name__)


class User(BaseModel, UserMixin):
    class Meta:
        table_name = 'users'

    created_by = ForeignKeyField('self', null=True, backref='children', column_name='created_by')
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
    roles = ManyToManyField(RoleModel, backref='users')

    def save(self, *args: list, **kwargs: dict) -> int:
        if self.password and 'password' in self._dirty:
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
            deleted_at = deleted_at.strftime('%Y-%m-%d %H:%M:%S')

        if isinstance(birth_date, date):
            birth_date = birth_date.strftime('%Y-%m-%d')

        roles = []
        for item in self.roles:
            role_data = item.serialize()
            roles.append(role_data)

        data = {
            'id': data.get('id'),
            'name': data.get('name'),
            'last_name': data.get('last_name'),
            'email': data.get('email'),
            'genre': data.get('genre'),
            'birth_date': birth_date,
            'active': active,
            'created_at': data.get('created_at').strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': data.get('updated_at').strftime('%Y-%m-%d %H:%M:%S'),
            'deleted_at': deleted_at,
            'created_by': data.get('created_by'),
            'roles': roles,
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

        url_safe_serializer = URLSafeSerializer(secret_key, salt)
        timestamp_signer = TimestampSigner(secret_key)

        data = url_safe_serializer.dumps({'user_id': self.id})
        return timestamp_signer.sign(data).decode('utf-8')

    @classmethod
    def get_fields(cls, exclude: list = None, include: list = None, sort_order: list = None) -> set:
        exclude = exclude or []
        include = include or []
        sort_order = sort_order or []

        fields = set(filter(
            lambda x: x not in exclude,
            list(cls._meta.fields)
        ))

        if include:
            fields = set(filter(
                lambda x: x in include,
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

        url_safe_serializer = URLSafeSerializer(secret_key, salt)
        timestamp_signer = TimestampSigner(secret_key)

        try:
            parsed_token = timestamp_signer.unsign(token, max_age=expire_in).decode('utf-8')
            user_id = url_safe_serializer.loads(parsed_token)['user_id']
        except:
            return None
        return User.get_or_none(user_id)

    @staticmethod
    def ensure_password(plain_text: str) -> str:
        hashed_password = None

        if plain_text:
            hashed_password = hash_password(plain_text)

        return hashed_password

UserRoles = User.roles.through_model

user_datastore = PeeweeUserDatastore(db, User, RoleModel, UserRoles)
