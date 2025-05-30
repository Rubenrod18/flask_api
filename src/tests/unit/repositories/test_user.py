from datetime import datetime

from app.database.factories.user_factory import UserFactory
from app.repositories.user import UserRepository
from tests.base.base_test import BaseTest


class UserRepositoryTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.repository = UserRepository()

    def test_create_user(self):
        user_data = UserFactory.build_dict(exclude=('roles',))

        user = self.repository.create(**user_data)

        self.assertEqual(user.name, user_data['name'])
        self.assertEqual(user.last_name, user_data['last_name'])
        self.assertEqual(user.email, user_data['email'])
        self.assertEqual(user.genre, user_data['genre'])
        self.assertEqual(user.birth_date, user_data['birth_date'])
        self.assertEqual(user.active, user_data['active'])

    def test_find_user(self):
        user = UserFactory()

        test_cases = [
            ('name', user.name),
            ('fs_uniquifier', user.fs_uniquifier),
            ('last_name', user.last_name),
            ('email', user.email),
            ('genre', user.genre),
            ('birth_date', user.birth_date),
            ('active', user.active),
            ('created_at', user.created_at),
            ('updated_at', user.updated_at),
            ('deleted_at', user.deleted_at),
        ]

        for field_name, field_value in test_cases:
            with self.subTest(msg=field_name, field_value=field_value):
                self.assertTrue(self.repository.find(**{field_name: field_value}))

    def test_delete_soft_user(self):
        user = UserFactory()

        user = self.repository.delete(user)

        self.assertTrue(isinstance(user.deleted_at, datetime))

    def test_delete_hard_user(self):
        user = UserFactory()

        with self.assertRaises(NotImplementedError):
            self.repository.delete(user, force_delete=True)
