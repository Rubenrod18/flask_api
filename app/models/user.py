import logging

from flask import current_app
from flask_security import hash_password
from flask_security import UserMixin
from itsdangerous import TimestampSigner
from itsdangerous import URLSafeSerializer
from peewee import BooleanField
from peewee import CharField
from peewee import DateField
from peewee import FixedCharField
from peewee import ForeignKeyField
from peewee import ManyToManyField
from peewee import TextField
from peewee import TimestampField

from .base import Base as BaseModel
from .role import Role as RoleModel

logger = logging.getLogger(__name__)


class User(BaseModel, UserMixin):
    """User database model.

    References
    ----------
    fs_uniquier field is required by flask-security-too:
    https://flask-security-too.readthedocs.io/en/stable/changelog.html#version-4-0-0

    """

    class Meta:
        table_name = 'users'

    fs_uniquifier = TextField(null=False)
    created_by = ForeignKeyField('self', null=True, backref='children', column_name='created_by')
    name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField(null=False)
    genre = FixedCharField(
        max_length=1,
        choices=(
            (
                'm',
                'male',
            ),
            ('f', 'female'),
        ),
        null=True,
    )
    birth_date = DateField()
    active = BooleanField(default=True)
    created_at = TimestampField(default=None)
    updated_at = TimestampField()
    deleted_at = TimestampField(default=None, null=True)
    roles = ManyToManyField(RoleModel, backref='users')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args: list, **kwargs: dict) -> int:
        if self.password and 'password' in self._dirty:
            self.password = self.ensure_password(self.password)

        return super().save(*args, **kwargs)

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
        except:  # noqa: E722
            # TODO: what kind of exception throws here?
            return None
        return User.get_or_none(user_id)

    @staticmethod
    def ensure_password(plain_text: str) -> str:
        return hash_password(plain_text) if plain_text else None
