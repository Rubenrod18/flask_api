import os

from app.extensions import db
from app.models import Role as RoleModel
from app.models import User as UserModel
from database import seed_actions
from database.factories.user_factory import UserFactory


class UserSeeder:
    name = 'UserSeeder'

    @staticmethod
    def _create_admin_user():
        test_user_email = os.getenv('TEST_USER_EMAIL')
        test_user = db.session.query(UserModel).filter(UserModel.email == test_user_email).first()

        if test_user is None:
            role = db.session.query(RoleModel).filter(RoleModel.name == 'admin').first()

            params = {
                'email': test_user_email,
                'password': UserModel.ensure_password(os.getenv('TEST_USER_PASSWORD')),
                'deleted_at': None,
                'active': True,
                'created_by': None,
                'roles': [role],
            }
            UserFactory.create(**params)

    @seed_actions
    def __init__(self, rows: int = 20):
        # save user with user_datastore and method
        # "create_user" -> look flask_security -> datastore.py
        self._create_admin_user()
        UserFactory.create_batch(rows)
