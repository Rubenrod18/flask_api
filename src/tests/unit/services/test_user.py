# pylint: disable=attribute-defined-outside-init, unused-argument
from datetime import datetime, UTC
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.models import User
from app.repositories import RoleRepository, UserRepository
from app.services import RoleService, UserService


class _TestUserBaseService:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.role = RoleFactory(deleted_at=None)
        self.user = UserFactory(deleted_at=None, roles=[self.role])


class TestCreateUserService(_TestUserBaseService):
    @mock.patch('app.services.user.current_user', autospec=True)
    @mock.patch('app.services.user.user_datastore.create_user', autospec=True)
    @mock.patch('app.services.user.db.session', autospec=True)
    def test_create_user(self, mock_session, mock_create_user, mock_current_user):
        mock_current_user.id = self.user.id
        mock_create_user.return_value = self.user

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_last_record.return_value = self.user
        mock_role_repository = MagicMock(spec=RoleRepository)
        mock_role_repository.find_by_id.return_value = self.role
        user_service = UserService(mock_user_repo, mock_role_repository)

        user_data = UserFactory.build_dict(exclude={'roles', 'created_by'})
        user_data['role_id'] = self.role.id

        created_user = user_service.create(**user_data)
        user_data.pop('role_id')
        user_data['created_by'] = 1
        user_data['fs_uniquifier'] = 2
        user_data['roles'] = [self.role]

        mock_user_repo.get_last_record.assert_called_once()
        mock_create_user.assert_called_once_with(**user_data)
        mock_session.add.assert_called_once_with(self.user)
        mock_session.flush.assert_called_once_with()
        mock_role_repository.find_by_id.assert_called_once_with(self.role.id)
        assert isinstance(created_user, User)
        assert created_user.created_by == self.user.created_by
        assert created_user.fs_uniquifier == self.user.fs_uniquifier
        assert created_user.name == self.user.name
        assert created_user.last_name == self.user.last_name
        assert created_user.email == self.user.email
        assert created_user.genre == self.user.genre
        assert created_user.birth_date == self.user.birth_date
        assert created_user.active == self.user.active
        assert created_user.created_at
        assert created_user.updated_at, created_user.created_at
        assert created_user.deleted_at is None
        assert created_user.roles[0].id == self.role.id


class TestFindByIdUserService(_TestUserBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.user = UserFactory(deleted_at=None, roles=[self.role])

    def test_find_by_id_user(self):
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.find_by_id.return_value = self.user
        user_service = UserService(mock_user_repo)

        user = user_service.find_by_id(self.user.id)

        mock_user_repo.find_by_id.assert_called_once_with(self.user.id)
        assert isinstance(user, User)
        assert user.id == self.user.id


class TestGetUserService(_TestUserBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.user = UserFactory(deleted_at=None, roles=[self.role])

    def test_get_user(self):
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get.return_value = [self.user]
        user_service = UserService(mock_user_repo)

        user_data = {
            'items_per_page': 10,
            'order': [{'field_name': 'name', 'sorting': 'asc'}, {'field_name': 'created_at', 'sorting': 'desc'}],
            'page_number': 1,
            'search': [{'field_name': 'name', 'field_operator': 'contains', 'field_value': 'n'}],
        }
        users = user_service.get(**user_data)

        mock_user_repo.get.assert_called_once_with(**user_data)
        assert len(users) == 1
        assert isinstance(users[0], User)
        assert users[0].id == self.user.id


class TestSaveUserService(_TestUserBaseService):
    @mock.patch('app.services.user.db.session', autospec=True)
    @mock.patch('app.services.user.user_datastore.remove_role_from_user', autospec=True)
    @mock.patch('app.services.user.user_datastore.add_role_to_user', autospec=True)
    @mock.patch('app.services.user.User.reload', autospec=True)
    def test_save_user(self, mock_user_reload, mock_add_role_to_user, mock_remove_role_from_user, mock_session):
        mock_user_reload.return_value = self.user

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.save.return_value = self.user
        mock_role_repository = MagicMock(spec=RoleService)
        mock_role_repository.find_by_id.return_value = self.role
        user_service = UserService(mock_user_repo, mock_role_repository)

        user_data = UserFactory.build_dict(exclude={'roles', 'created_by'})
        user_data['role_id'] = self.role.id

        updated_user = user_service.save(self.user.id, **user_data)

        mock_user_repo.save.assert_called_once_with(
            self.user.id,
            **user_data,
        )
        mock_session.flush.assert_called_once_with()
        mock_remove_role_from_user.assert_called_once_with(self.user, self.user.roles[0])
        mock_add_role_to_user.assert_called_once_with(self.user, self.role)
        mock_role_repository.find_by_id.assert_called_once_with(self.role.id)
        mock_user_reload.assert_called_once()
        assert isinstance(updated_user, User)
        assert updated_user.created_by == self.user.created_by
        assert updated_user.fs_uniquifier == self.user.fs_uniquifier
        assert updated_user.name == self.user.name
        assert updated_user.last_name == self.user.last_name
        assert updated_user.email == self.user.email
        assert updated_user.genre == self.user.genre
        assert updated_user.birth_date == self.user.birth_date
        assert updated_user.active == self.user.active
        assert updated_user.created_at
        assert updated_user.updated_at, updated_user.created_at
        assert updated_user.deleted_at is None

    @mock.patch('app.services.user.db.session', autospec=True)
    @mock.patch('app.services.user.user_datastore.remove_role_from_user', autospec=True)
    @mock.patch('app.services.user.user_datastore.add_role_to_user', autospec=True)
    @mock.patch('app.services.user.User.reload', autospec=True)
    def test_save_user_no_role_id(
        self, mock_user_reload, mock_add_role_to_user, mock_remove_role_from_user, mock_session
    ):
        mock_user_reload.return_value = self.user

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.save.return_value = self.user
        mock_role_repository = MagicMock(spec=RoleService)
        user_service = UserService(mock_user_repo, mock_role_repository)

        user_data = UserFactory.build_dict(exclude={'roles', 'created_by'})

        updated_user = user_service.save(self.user.id, **user_data)

        mock_user_repo.save.assert_called_once_with(
            self.user.id,
            **user_data,
        )
        mock_session.flush.assert_called_once_with()
        mock_add_role_to_user.assert_not_called()
        mock_role_repository.assert_not_called()
        mock_remove_role_from_user.assert_not_called()
        mock_user_reload.assert_called_once()
        assert isinstance(updated_user, User)
        assert updated_user.created_by == self.user.created_by
        assert updated_user.fs_uniquifier == self.user.fs_uniquifier
        assert updated_user.name == self.user.name
        assert updated_user.last_name == self.user.last_name
        assert updated_user.email == self.user.email
        assert updated_user.genre == self.user.genre
        assert updated_user.birth_date == self.user.birth_date
        assert updated_user.active == self.user.active
        assert updated_user.created_at
        assert updated_user.updated_at == updated_user.created_at
        assert updated_user.deleted_at is None


class TestDeleteUserService(_TestUserBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.user = UserFactory(deleted_at=None, roles=[self.role])

    def test_delete_user(self):
        mock_user_repo = MagicMock(spec=UserRepository)
        self.user.deleted_at = datetime.now(UTC)
        mock_user_repo.delete.return_value = self.user
        user_service = UserService(mock_user_repo)

        user = user_service.delete(self.user.id)

        mock_user_repo.delete.assert_called_once_with(self.user.id)
        assert isinstance(user, User)
        assert user.id == self.user.id
        assert user.deleted_at == self.user.deleted_at
