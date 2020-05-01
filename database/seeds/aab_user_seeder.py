import os

from app.models.user import User as UserModel
from database.factories import Factory
from database.seeds import seed_actions


class UserSeeder():
    __name__ = 'UserSeeder'

    @seed_actions
    def __init__(self, rows: int = 10):
        Factory('User', rows).save()

        test_user_email = os.getenv('TEST_USER_EMAIL')
        test_user = UserModel.get_or_none(email=test_user_email)

        if test_user is None:
            kwargs = {
                'email': test_user,
                'password': os.getenv('TEST_USER_PASSWORD'),
                'deleted_at': None,
                'active': True,
            }

            Factory('User').save(**kwargs)
