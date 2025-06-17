from datetime import datetime, UTC

import pytest

from app.database.factories.user_factory import AdminUserFactory, UserFactory
from app.extensions import db
from app.models import User
from app.repositories.user import UserRepository


class TestUserRepository:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.repository = UserRepository()

    def test_create_user(self):
        with pytest.raises(NotImplementedError):
            self.repository.create(**{})

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
            result = self.repository.find(*args, **kwargs)
            assert result is not None, (description, args, kwargs)
            assert isinstance(result, User), (description, args, kwargs)
            assert result.id == user.id, (description, args, kwargs)

    def test_find_by_email_user(self):
        user = UserFactory(
            deleted_at=datetime.now(UTC), created_by_user=AdminUserFactory(deleted_at=None, active=True), active=False
        )

        test_cases = [
            ('fs_uniquifier', (User.fs_uniquifier == user.fs_uniquifier,)),
            ('created_by', (User.created_by == user.created_by_user.id,)),
            ('name', (User.name == user.name,)),
            ('last_name', (User.last_name == user.last_name,)),
            ('genre', (User.genre == user.genre,)),
            ('birth_date', (User.birth_date == user.birth_date,)),
            ('active', (User.active == user.active,)),
            ('created_at', (User.created_at == user.created_at,)),
            ('updated_at', (User.updated_at == user.updated_at,)),
            ('deleted_at', (User.deleted_at == user.deleted_at,)),
        ]

        for description, args in test_cases:
            result = self.repository.find_by_email(user.email, *args)
            assert result is not None, (description, args)
            assert isinstance(result, User), (description, args)
            assert result.id == user.id, (description, args)

    def test_find_by_email_not_found_user(self):
        UserFactory(
            deleted_at=datetime.now(UTC), created_by_user=AdminUserFactory(deleted_at=None, active=True), active=False
        )

        found_user = self.repository.find_by_email('fake-user@mail.com')

        assert found_user is None

    def test_get_last_record_user(self):
        UserFactory(deleted_at=datetime.now(UTC), created_by_user=None, active=False)
        UserFactory(
            deleted_at=datetime.now(UTC), created_by_user=AdminUserFactory(deleted_at=None, active=True), active=False
        )

        found_user = self.repository.get_last_record()

        assert found_user is not None
        assert isinstance(found_user, User)
        assert found_user.id == 3

    def test_delete_soft_user(self):
        user = UserFactory()

        user = self.repository.delete(user.id)

        assert isinstance(user.deleted_at, datetime)
        assert db.session.query(User).filter_by(name=user.name, deleted_at=user.deleted_at).one_or_none() is None

    def test_delete_hard_user(self):
        user = UserFactory()

        with pytest.raises(NotImplementedError):
            self.repository.delete(user.id, force_delete=True)
