import os

from app.extensions import db_wrapper
from app.models import Role as RoleModel, User as UserModel
from database import seed_actions
from database.factories import Factory


class UserSeeder:
    name = 'UserSeeder'

    @staticmethod
    def _create_admin_user():
        test_user_email = os.getenv('TEST_USER_EMAIL')
        test_user = UserModel.get_or_none(email=test_user_email)

        if test_user is None:
            role = RoleModel.get_by_id(1)

            params = {
                'email': test_user_email,
                'password': os.getenv('TEST_USER_PASSWORD'),
                'deleted_at': None,
                'active': True,
                'created_by': None,
                'roles': [role],
            }
            Factory('User').save(params)

    @seed_actions
    def __init__(self, rows: int = 30):
        # save user with user_datastore and method "create_user" -> look flask_security -> datastore.py
        with db_wrapper.database.atomic():
            self._create_admin_user()
            Factory('User', rows).save()
