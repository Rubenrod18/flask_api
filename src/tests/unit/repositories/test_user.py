from datetime import datetime, UTC

from app.database.factories.user_factory import AdminUserFactory, UserFactory
from app.extensions import db
from app.models import User
from app.repositories.user import UserRepository
from tests.base.base_test import BaseTest


class UserRepositoryTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.repository = UserRepository()

    def test_create_user(self):
        user_data = UserFactory.build_dict(exclude={'roles'})

        user = self.repository.create(**user_data)

        self.assertEqual(user.name, user_data['name'])
        self.assertEqual(user.last_name, user_data['last_name'])
        self.assertEqual(user.email, user_data['email'])
        self.assertEqual(user.genre, user_data['genre'])
        self.assertEqual(user.birth_date, user_data['birth_date'])
        self.assertEqual(user.active, user_data['active'])
        self.assertIsNone(db.session.query(User).filter_by(name=user_data['name']).one_or_none())

    def test_find_user(self):
        admin = AdminUserFactory(deleted_at=None, active=True)
        user = UserFactory(deleted_at=datetime.now(UTC), created_by_user=admin, active=False)

        test_cases = [
            ('id', (), {'id': user.id}),
            ('fs_uniquifier', (), {'fs_uniquifier': user.fs_uniquifier}),
            ('created_by', (), {'created_by': user.created_by_user.id}),
            ('name', (), {'name': user.name}),
            ('last_name', (), {'last_name': user.last_name}),
            ('email', (), {'email': user.email}),
            ('genre', (), {'genre': user.genre}),
            ('birth_date', (), {'birth_date': user.birth_date}),
            ('active', (), {'active': user.active}),
            ('created_at', (), {'created_at': user.created_at}),
            ('updated_at', (), {'updated_at': user.updated_at}),
            ('deleted_at', (), {'deleted_at': user.deleted_at}),
            ('id', (User.id == user.id,), {}),
            ('fs_uniquifier', (User.fs_uniquifier == user.fs_uniquifier,), {}),
            ('created_by', (User.created_by == user.created_by_user.id,), {}),
            ('name', (User.name == user.name,), {}),
            ('last_name', (User.last_name == user.last_name,), {}),
            ('email', (User.email == user.email,), {}),
            ('genre', (User.genre == user.genre,), {}),
            ('birth_date', (User.birth_date == user.birth_date,), {}),
            ('active', (User.active == user.active,), {}),
            ('created_at', (User.created_at == user.created_at,), {}),
            ('updated_at', (User.updated_at == user.updated_at,), {}),
            ('deleted_at', (User.deleted_at == user.deleted_at,), {}),
        ]

        for description, args, kwargs in test_cases:
            with self.subTest():
                result = self.repository.find(*args, **kwargs)
                self.assertIsNotNone(result, (description, args, kwargs))
                self.assertTrue(isinstance(result, User), (description, args, kwargs))
                self.assertEqual(result.id, user.id, (description, args, kwargs))

    def test_delete_soft_user(self):
        user = UserFactory()

        user = self.repository.delete(user)

        self.assertTrue(isinstance(user.deleted_at, datetime))
        self.assertIsNone(db.session.query(User).filter_by(name=user.name, deleted_at=user.deleted_at).one_or_none())

    def test_delete_hard_user(self):
        user = UserFactory()

        with self.assertRaises(NotImplementedError):
            self.repository.delete(user, force_delete=True)
