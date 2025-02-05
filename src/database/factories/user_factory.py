from datetime import timedelta
import os
import random
from random import randint
from typing import List

import factory
from sqlalchemy import func

from app.extensions import db
from app.managers import UserManager
from app.models import User as UserModel, Role as RoleModel
from app.models.user import Genre

from database.factories.base_factory import BaseFactory, faker
from database.factories.role_factory import AdminRoleFactory

UserList = List[UserModel]
_user_manager = UserManager()


class UserFactory(BaseFactory):
    class Meta:
        model = UserModel

    fs_uniquifier = factory.Faker('uuid4')
    name = factory.Faker('name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    genre = factory.Iterator(Genre.to_list())
    birth_date = faker.date_time_between(start_date='-30y', end_date='-5y')
    active = factory.Faker('boolean')

    @factory.lazy_attribute
    def password(self):
        return UserModel.ensure_password(os.getenv('TEST_USER_PASSWORD'))

    @factory.lazy_attribute
    def created_by(self):
        user = (
            db.session.query(UserModel)
            .join(UserModel.roles)
            .filter(UserModel.deleted_at.is_(None), RoleModel.name == 'admin')
            .order_by(func.random())
            .limit(1)
            .one_or_none()
        )
        return None if user is None else user.id

    @factory.lazy_attribute
    def roles(self):
        return [
            db.session.query(RoleModel)
            .filter(RoleModel.deleted_at.is_(None))
            .order_by(func.random())
            .limit(1)
            .first()
        ]

    @factory.lazy_attribute
    def created_at(self):
        return faker.date_time_between(start_date='-3y', end_date='now')

    @factory.lazy_attribute
    def deleted_at(self):
        return random.choice([faker.date_time_between(start_date='-1y', end_date='now'), None])

    @factory.lazy_attribute
    def updated_at(self):
        if self.deleted_at:
            updated_at = self.deleted_at
        else:
            updated_at = self.created_at + timedelta(days=randint(1, 30), minutes=randint(0, 60))
        return updated_at


class AdminUserFactory(UserFactory):
    @factory.lazy_attribute
    def roles(self):
        return [AdminRoleFactory()]
