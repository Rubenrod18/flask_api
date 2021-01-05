from datetime import datetime, timedelta
from random import randint
from typing import TypeVar, List

from flask import current_app
from peewee import fn
from playhouse.shortcuts import model_to_dict

from app.models import Role as RoleModel, User as UserModel, user_datastore
from app.utils import ignore_keys
from database import fake

T = TypeVar('T', UserModel, dict)
UserList = List[UserModel]


class _UserFactory:
    @staticmethod
    def _fill(params: dict, to_dict: bool, exclude: list) -> dict:
        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.utcnow()

        created_at = current_date - timedelta(days=randint(31, 100),
                                              minutes=randint(0, 60))
        updated_at = created_at
        deleted_at = None

        if randint(0, 1) and 'deleted_at' not in params:
            deleted_at = created_at + timedelta(days=randint(1, 30),
                                                minutes=randint(0, 60))
        else:
            updated_at = created_at + timedelta(days=randint(1, 30),
                                                minutes=randint(0, 60))

        if 'created_by' not in params:
            created_by = (UserModel.select()
                          .where(UserModel.created_by.is_null())
                          .order_by(fn.Random())
                          .limit(1)
                          .get()
                          .id)
        else:
            created_by = None

        data = {
            'created_by': params.get('created_by') or created_by,
            'name': params.get('name') or fake.name(),
            'last_name': params.get('last_name') or fake.last_name(),
            'email': params.get('email') or fake.random_element(
                [fake.email(), fake.safe_email(), fake.free_email(),
                 fake.company_email()]),
            'genre': params.get('genre') or fake.random_element(['m', 'f']),
            'password': params.get('password') or current_app.config.get('TEST_USER_PASSWORD'),
            'birth_date': params.get('birth_date') or birth_date.strftime('%Y-%m-%d'),
            'active': params.get('active') or fake.boolean(),
            'created_at': created_at,
            'updated_at': updated_at,
            'deleted_at': deleted_at,
        }

        if to_dict:
            data['created_at'] = data.get('created_at').strftime('%Y-%m-%d %H:%M:%S')
            data['updated_at'] = data.get('updated_at').strftime('%Y-%m-%d %H:%M:%S')
            if data.get('deleted_at'):
                data['deleted_at'] = data.get('deleted_at').strftime('%Y-%m-%d %H:%M:%S')

        return ignore_keys(data, exclude)

    def make(self, params: dict, to_dict: bool, exclude: list) -> T:
        data = self._fill(params, to_dict, exclude)

        if to_dict:
            user = data
        else:
            user = UserModel()
            user.created_by = data.get('created_by')
            user.name = data.get('name')
            user.last_name = data.get('last_name')
            user.email = data.get('email')
            user.genre = data.get('genre')
            user.password = data.get('password')
            user.birth_date = data.get('birth_date')
            user.active = data.get('active')
            user.created_at = data.get('created_at')
            user.updated_at = data.get('updated_at')
            user.deleted_at = data.get('deleted_at')

        return user

    def create(self, params: dict) -> UserModel:
        data = model_to_dict(self.make(params, to_dict=False, exclude=[]),
                             recurse=False)

        # Roles are required for flask_security.datastore
        if 'roles' in params:
            roles = params['roles']
        else:
            role = (RoleModel.select()
                    .where(RoleModel.deleted_at.is_null())
                    .order_by(fn.Random())
                    .limit(1)
                    .get())
            roles = [role]
        data['roles'] = roles

        return user_datastore.create_user(**data)

    def bulk_create(self, total: int, params: dict) -> UserList:
        data = []

        for item in range(total):
            user = self.create(params)
            data.append(user)

        return data
