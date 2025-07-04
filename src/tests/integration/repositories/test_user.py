from datetime import datetime, UTC

import pytest

from app.extensions import db
from app.models import User
from app.repositories.user import UserRepository
from tests.factories.user_factory import AdminUserFactory, UserFactory


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestUserRepository:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.repository = UserRepository()

    def test_create_user(self):
        with pytest.raises(NotImplementedError):
            self.repository.create(**{})

    @pytest.mark.parametrize(
        'field, args, kwargs',
        [
            ('id', (), lambda user: {'id': user.id}),
            ('fs_uniquifier', (), lambda user: {'fs_uniquifier': user.fs_uniquifier}),
            ('created_by', (), lambda user: {'created_by': user.created_by_user.id}),
            ('name', (), lambda user: {'name': user.name}),
            ('last_name', (), lambda user: {'last_name': user.last_name}),
            ('email', (), lambda user: {'email': user.email}),
            ('genre', (), lambda user: {'genre': user.genre}),
            ('birth_date', (), lambda user: {'birth_date': user.birth_date}),
            ('active', (), lambda user: {'active': user.active}),
            ('created_at', (), lambda user: {'created_at': user.created_at}),
            ('updated_at', (), lambda user: {'updated_at': user.updated_at}),
            ('deleted_at', (), lambda user: {'deleted_at': user.deleted_at}),
            ('id_expr', lambda user: (User.id == user.id,), lambda user: {}),
            ('fs_uniquifier_expr', lambda user: (User.fs_uniquifier == user.fs_uniquifier,), lambda user: {}),
            ('created_by_expr', lambda user: (User.created_by == user.created_by_user.id,), lambda user: {}),
            ('name_expr', lambda user: (User.name == user.name,), lambda user: {}),
            ('last_name_expr', lambda user: (User.last_name == user.last_name,), lambda user: {}),
            ('email_expr', lambda user: (User.email == user.email,), lambda user: {}),
            ('genre_expr', lambda user: (User.genre == user.genre,), lambda user: {}),
            ('birth_date_expr', lambda user: (User.birth_date == user.birth_date,), lambda user: {}),
            ('active_expr', lambda user: (User.active == user.active,), lambda user: {}),
            ('created_at_expr', lambda user: (User.created_at == user.created_at,), lambda user: {}),
            ('updated_at_expr', lambda user: (User.updated_at == user.updated_at,), lambda user: {}),
            ('deleted_at_expr', lambda user: (User.deleted_at == user.deleted_at,), lambda user: {}),
        ],
    )
    def test_find_user(self, field, args, kwargs):
        admin = AdminUserFactory(deleted_at=None, active=True)
        user = UserFactory(deleted_at=datetime.now(UTC), created_by_user=admin, active=False)
        args = args(user) if callable(args) else args
        kwargs = kwargs(user) if callable(kwargs) else kwargs

        result = self.repository.find(*args, **kwargs)

        assert result is not None, (field, args, kwargs)
        assert isinstance(result, User)
        assert result.id == user.id

    @pytest.mark.parametrize(
        'field, expression',
        [
            ('fs_uniquifier', lambda u: (User.fs_uniquifier == u.fs_uniquifier,)),
            ('created_by', lambda u: (User.created_by == u.created_by_user.id,)),
            ('name', lambda u: (User.name == u.name,)),
            ('last_name', lambda u: (User.last_name == u.last_name,)),
            ('genre', lambda u: (User.genre == u.genre,)),
            ('birth_date', lambda u: (User.birth_date == u.birth_date,)),
            ('active', lambda u: (User.active == u.active,)),
            ('created_at', lambda u: (User.created_at == u.created_at,)),
            ('updated_at', lambda u: (User.updated_at == u.updated_at,)),
            ('deleted_at', lambda u: (User.deleted_at == u.deleted_at,)),
        ],
    )
    def test_find_by_email_user(self, field, expression):
        user = UserFactory(
            deleted_at=datetime.now(UTC), created_by_user=AdminUserFactory(deleted_at=None, active=True), active=False
        )
        expr = expression(user)

        result = self.repository.find_by_email(user.email, *expr)

        assert result is not None, (field, expr)
        assert isinstance(result, User)
        assert result.id == user.id

    def test_find_by_email_not_found_user(self):
        UserFactory(
            deleted_at=datetime.now(UTC), created_by_user=AdminUserFactory(deleted_at=None, active=True), active=False
        )
        found_user = self.repository.find_by_email('fake-user@mail.com')
        assert found_user is None

    def test_get_last_record_user(self):
        UserFactory(deleted_at=datetime.now(UTC), created_by_user=None, active=False)
        last_user = UserFactory(
            deleted_at=datetime.now(UTC), created_by_user=AdminUserFactory(deleted_at=None, active=True), active=False
        )
        found_user = self.repository.get_last_record()
        assert found_user is not None
        assert isinstance(found_user, User)
        assert found_user.id == last_user.id

    def test_delete_soft_user(self):
        user = UserFactory()
        deleted_user = self.repository.delete(user.id)
        assert isinstance(deleted_user.deleted_at, datetime)
        assert db.session.query(User).filter_by(name=user.name, deleted_at=user.deleted_at).one_or_none() is None

    def test_delete_hard_user(self):
        user = UserFactory()
        with pytest.raises(NotImplementedError):
            self.repository.delete(user.id, force_delete=True)
