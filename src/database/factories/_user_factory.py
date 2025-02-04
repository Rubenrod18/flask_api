from datetime import UTC, datetime, timedelta
from random import randint
from typing import TypeVar, List

from flask import current_app
from sqlalchemy import func

from app.extensions import db
from app.models import Role as RoleModel, User as UserModel, user_datastore
from app.utils import ignore_keys
from database import fake
from database.factories import serialize_dict

T = TypeVar('T', UserModel, dict)
UserList = List[UserModel]


class _UserFactory:
    @staticmethod
    def _fill(params: dict, to_dict: bool, exclude: list) -> dict:
        def generate_fake_user_email():
            fake_email = fake.random_element([fake.email(),
                                              fake.safe_email(),
                                              fake.free_email(),
                                              fake.company_email()])
            return f'%s_{fake_email}' % randint(1, 9999)

        birth_date = fake.date_between(start_date='-50y', end_date='-5y')
        current_date = datetime.now(UTC)

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
            with db.session.no_autoflush:
                created_by = (
                    db.session.query(UserModel).filter(UserModel.created_by.is_(None)).order_by(func.random()).limit(1).first()
                    .id
                )
        else:
            created_by = None

        with db.session.no_autoflush:
            user = (
                db.session.query(UserModel)
                .order_by(UserModel.id.desc())
                .limit(1)
                .first()
            )
        fs_uniquifier = 1 if user is None else user.id + 1

        data = {
            'fs_uniquifier': fs_uniquifier,
            'created_by': params.get('created_by') or created_by,
            'name': params.get('name') or fake.name(),
            'last_name': params.get('last_name') or fake.last_name(),
            'email': params.get('email') or generate_fake_user_email(),
            'genre': params.get('genre') or fake.random_element(['m', 'f']),
            'password': params.get('password') or current_app.config.get('TEST_USER_PASSWORD'),
            'birth_date': params.get('birth_date') or birth_date,
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
            user = serialize_dict(data)
        else:
            model_data = {
                item: data.get(item)
                for item in UserModel.get_fields(exclude)
            }
            user = UserModel(**model_data)

        return user

    def create(self, params: dict) -> UserModel:
        def model_to_dict(instance):
            """Convert an SQLAlchemy model instance into a dictionary."""
            return {column.name: getattr(instance, column.name) for column in instance.__table__.columns}

        data = model_to_dict(self.make(params, to_dict=False, exclude=[]))

        # Roles are required for flask_security.datastore
        if 'roles' in params:
            roles = params['roles']
        else:
            role = (
                db.session.query(RoleModel)
                .filter(RoleModel.deleted_at.is_(None))
                .order_by(func.random())
                .limit(1)
                .first()
            )
            roles = [role]
        data['roles'] = roles

        return user_datastore.create_user(**data)

    def bulk_create(self, total: int, params: dict) -> UserList:
        data = []

        for item in range(total):
            user = self.create(params)
            data.append(user)

        db.session.add_all(data)
        return data
