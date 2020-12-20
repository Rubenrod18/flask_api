import logging

from flask import current_app
from flask_security import UserMixin, hash_password
from itsdangerous import URLSafeSerializer, TimestampSigner
from peewee import (CharField, DateField, TimestampField, ForeignKeyField,
                    BooleanField, FixedCharField, ManyToManyField)

from .base import Base as BaseModel
from .role import Role as RoleModel

logger = logging.getLogger(__name__)


class User(BaseModel, UserMixin):
    class Meta:
        table_name = 'users'

    created_by = ForeignKeyField('self', null=True, backref='children',
                                 column_name='created_by')
    name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField(null=False)
    genre = FixedCharField(max_length=1,
                           choices=(('m', 'male',), ('f', 'female')), null=True)
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

    def get_reset_token(self) -> str:
        secret_key = current_app.config.get('SECRET_KEY')
        expire_in = current_app.config.get('RESET_TOKEN_EXPIRES')
        salt = expire_in.__str__()

        url_safe_serializer = URLSafeSerializer(secret_key, salt)
        timestamp_signer = TimestampSigner(secret_key)

        data = url_safe_serializer.dumps({'user_id': self.id})
        return timestamp_signer.sign(data).decode('utf-8')

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
