# pylint: disable=attribute-defined-outside-init, unused-argument
import random
from datetime import datetime, UTC
from types import SimpleNamespace
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.models.user import Genre
from app.repositories import RoleRepository, UserRepository
from app.services import RoleService, UserService
from tests.base.base_unit_test import TestBaseUnit


class _UserStub(SimpleNamespace):
    def reload(self):
        return True


class _TestUserBaseService(TestBaseUnit):
    @pytest.fixture(autouse=True)
    def base_setup(self, faker):
        self.user_id = faker.random_int()
        self.role_id = faker.random_int()
        self.role = MagicMock(SimpleNamespace, autospec=True)
        self.user = MagicMock(_UserStub, autospec=True)


class TestCreateUserService(_TestUserBaseService):
    @mock.patch('app.services.user.current_user', autospec=True)
    @mock.patch('app.services.user.user_datastore.create_user', autospec=True)
    @mock.patch('app.services.user.db.session')
    @mock.patch('app.services.user.uuid.uuid4', autospec=True)
    def test_create_user(self, mock_uuid4, mock_session, mock_create_user, mock_current_user):
        mock_current_user.id = self.user_id
        mock_create_user.return_value = self.user
        fs_uniquifier = str(self.faker.uuid4())
        mock_uuid4.return_value = fs_uniquifier

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_role_repository = MagicMock(spec=RoleRepository)
        mock_role_repository.find_by_id.return_value = self.role
        user_service = UserService(mock_user_repo, mock_role_repository)

        user_data = {
            'name': self.faker.name(),
            'last_name': self.faker.last_name(),
            'email': self.faker.email(),
            'genre': random.choice(Genre.to_list()),
            'birth_date': self.faker.date_time_between(start_date='-30y', end_date='-5y'),
            'active': self.faker.boolean(),
            'role_id': self.role_id,
        }

        created_user = user_service.create(**user_data)
        user_data.pop('role_id')
        user_data['created_by'] = self.user_id
        user_data['fs_uniquifier'] = fs_uniquifier
        user_data['roles'] = [self.role]

        mock_uuid4.assert_called_once()
        mock_create_user.assert_called_once_with(**user_data)
        mock_session.add.assert_called_once_with(self.user)
        mock_session.flush.assert_called_once_with()
        mock_role_repository.find_by_id.assert_called_once_with(self.role_id)
        assert isinstance(created_user, _UserStub)


class TestFindByIdUserService(_TestUserBaseService):
    def test_find_by_id_user(self):
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.find_by_id.return_value = self.user
        user_service = UserService(mock_user_repo)

        user = user_service.find_by_id(self.user_id)

        mock_user_repo.find_by_id.assert_called_once_with(self.user_id)
        assert isinstance(user, _UserStub)


class TestGetUserService(_TestUserBaseService):
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
        assert isinstance(users[0], _UserStub)


class TestSaveUserService(_TestUserBaseService):
    @mock.patch('app.services.user.db.session')
    @mock.patch('app.services.user.user_datastore.remove_role_from_user', autospec=True)
    @mock.patch('app.services.user.user_datastore.add_role_to_user', autospec=True)
    def test_save_user(self, mock_add_role_to_user, mock_remove_role_from_user, mock_session):
        self.user.reload.return_value = self.user
        self.user.roles = [self.role]

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.save.return_value = self.user
        mock_role_repository = MagicMock(spec=RoleService)
        mock_role_repository.find_by_id.return_value = self.role
        user_service = UserService(mock_user_repo, mock_role_repository)

        user_data = {
            'name': self.faker.name(),
            'last_name': self.faker.last_name(),
            'email': self.faker.email(),
            'genre': random.choice(Genre.to_list()),
            'birth_date': self.faker.date_time_between(start_date='-30y', end_date='-5y'),
            'active': self.faker.boolean(),
            'role_id': self.role_id,
        }

        updated_user = user_service.save(self.user_id, **user_data)

        mock_user_repo.save.assert_called_once_with(
            self.user_id,
            **user_data,
        )
        mock_session.flush.assert_called_once_with()
        mock_remove_role_from_user.assert_called_once_with(self.user, self.user.roles[0])
        mock_add_role_to_user.assert_called_once_with(self.user, self.role)
        mock_role_repository.find_by_id.assert_called_once_with(self.role_id)
        self.user.reload.assert_called_once()
        assert isinstance(updated_user, _UserStub)

    @mock.patch('app.services.user.db.session')
    @mock.patch('app.services.user.user_datastore.remove_role_from_user', autospec=True)
    @mock.patch('app.services.user.user_datastore.add_role_to_user', autospec=True)
    def test_save_user_no_role_id(self, mock_add_role_to_user, mock_remove_role_from_user, mock_session):
        self.user.reload.return_value = self.user

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.save.return_value = self.user
        mock_role_repository = MagicMock(spec=RoleService)
        user_service = UserService(mock_user_repo, mock_role_repository)

        user_data = {
            'name': self.faker.name(),
            'last_name': self.faker.last_name(),
            'email': self.faker.email(),
            'genre': random.choice(Genre.to_list()),
            'birth_date': self.faker.date_time_between(start_date='-30y', end_date='-5y'),
            'active': self.faker.boolean(),
        }

        updated_user = user_service.save(self.user_id, **user_data)

        mock_user_repo.save.assert_called_once_with(
            self.user_id,
            **user_data,
        )
        mock_session.flush.assert_called_once_with()
        mock_add_role_to_user.assert_not_called()
        mock_role_repository.assert_not_called()
        mock_remove_role_from_user.assert_not_called()
        self.user.reload.assert_called_once()
        assert isinstance(updated_user, _UserStub)


class TestDeleteUserService(_TestUserBaseService):
    def test_delete_user(self):
        mock_user_repo = MagicMock(spec=UserRepository)
        self.user.deleted_at = datetime.now(UTC)
        mock_user_repo.delete.return_value = self.user
        user_service = UserService(mock_user_repo)

        user = user_service.delete(self.user_id)

        mock_user_repo.delete.assert_called_once_with(self.user_id)
        assert isinstance(user, _UserStub)
