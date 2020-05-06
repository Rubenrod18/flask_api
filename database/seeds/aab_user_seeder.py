import os

from app.models.user import User as UserModel
from database.factories import Factory
from database.seeds import seed_actions


class UserSeeder():
    name = 'UserSeeder'

    @seed_actions
    def __init__(self, rows: int = 10):
        test_user_email = os.getenv('TEST_USER_EMAIL')
        test_user = UserModel.get_or_none(email=test_user_email)

        if test_user is None:
            params = {
                'email': test_user_email,
                'password': os.getenv('TEST_USER_PASSWORD'),
                'deleted_at': None,
                'active': True,
                'created_by': None,
            }
            Factory('User').save(params)

        Factory('User', rows).save()
