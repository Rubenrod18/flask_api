import logging
import uuid

import sqlalchemy as sa
from flask_security import hash_password, SQLAlchemyUserDatastore, UserMixin
from sqlalchemy.orm import backref, relationship

from ..extensions import db
from ..utils.constants import BaseEnum
from .base import Base
from .role import Role

logger = logging.getLogger(__name__)


class Genre(BaseEnum):
    MALE = 'm'
    FEMALE = 'f'

    def __str__(self):
        return self.value


class User(Base, UserMixin):
    """User database model.

    References
    ----------
    fs_uniquier field is required by flask-security-too:
    https://flask-security-too.readthedocs.io/en/stable/changelog.html#version-4-0-0

    """

    __tablename__ = 'users'

    fs_uniquifier = sa.Column(sa.String(64), unique=True, nullable=False, default=uuid.uuid4())
    created_by = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=True)

    name = sa.Column(sa.String(255), nullable=False)
    last_name = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(255), nullable=False, unique=True)
    password = sa.Column(sa.String(255), nullable=False)
    genre = sa.Column(sa.String(1))
    birth_date = sa.Column(sa.Date, nullable=False)
    active = sa.Column(sa.Boolean, nullable=False)

    created_by_user = relationship('User', remote_side='User.id')
    roles = relationship('Role', secondary='users_roles_through', backref=backref('users', lazy='dynamic'))

    def save(self, *args: list, **kwargs: dict) -> int:
        if self.password and 'password' in self.__dict__:
            self.password = self.ensure_password(self.password)

        return super().save(*args, **kwargs)

    @staticmethod
    def ensure_password(plain_text: str) -> str:
        return hash_password(plain_text) if plain_text else None


class UsersRolesThrough(Base):
    __tablename__ = 'users_roles_through'

    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    role_id = sa.Column(sa.Integer, sa.ForeignKey('roles.id'))


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
