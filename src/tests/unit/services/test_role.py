# pylint: disable=attribute-defined-outside-init, unused-argument
from datetime import datetime, UTC
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import AdminUserFactory
from app.models import Role
from app.repositories import RoleRepository
from app.services import RoleService


class _TestRoleBaseService:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.admin_user = AdminUserFactory(deleted_at=None)


class TestCreateRoleService(_TestRoleBaseService):
    @mock.patch('app.services.role.db.session', autospec=True)
    def test_create_role(self, mock_session):
        mock_role_repo = MagicMock(spec=RoleRepository)
        role = RoleFactory(deleted_at=None)
        mock_role_repo.create.return_value = role
        role_service = RoleService(mock_role_repo)

        role_data = RoleFactory.build_dict()

        created_role = role_service.create(**role_data)

        mock_role_repo.create.assert_called_once_with(**role_data)
        mock_session.add.assert_called_once_with(role)
        mock_session.flush.assert_called_once_with()
        assert isinstance(created_role, Role)
        assert created_role.name, role.name
        assert created_role.description, role.description
        assert created_role.label, role.label
        assert created_role.created_at
        assert created_role.updated_at, created_role.created_at
        assert created_role.deleted_at is None


class TestFindByIdRoleService(_TestRoleBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = RoleFactory(deleted_at=None)

    def test_find_by_id_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        mock_role_repo.find_by_id.return_value = self.role
        role_service = RoleService(mock_role_repo)

        role = role_service.find_by_id(self.role.id)

        mock_role_repo.find_by_id.assert_called_once_with(self.role.id)
        assert isinstance(role, Role)
        assert role.id == self.role.id


class TestGetRoleService(_TestRoleBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = RoleFactory(deleted_at=None)

    def test_get_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        mock_role_repo.get.return_value = [self.role]
        role_service = RoleService(mock_role_repo)

        role_data = {
            'items_per_page': 10,
            'order': [{'field_name': 'name', 'sorting': 'asc'}, {'field_name': 'created_at', 'sorting': 'desc'}],
            'page_number': 1,
            'search': [{'field_name': 'name', 'field_operator': 'contains', 'field_value': 'n'}],
        }
        roles = role_service.get(**role_data)

        mock_role_repo.get.assert_called_once_with(**role_data)
        assert len(roles) == 1
        assert isinstance(roles[0], Role)
        assert roles[0].id == self.role.id


class TestSaveRoleService(_TestRoleBaseService):
    def test_save_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        role = RoleFactory(deleted_at=None)
        mock_role_repo.save.return_value = role
        role_service = RoleService(mock_role_repo)

        role_data = RoleFactory.build_dict()

        updated_role = role_service.save(role.id, **role_data)

        mock_role_repo.save.assert_called_once_with(
            role.id,
            **role_data,
        )
        assert isinstance(updated_role, Role)
        assert updated_role.name == role.name
        assert updated_role.description == role.description
        assert updated_role.label == role.label
        assert updated_role.created_at
        assert updated_role.updated_at, updated_role.created_at
        assert updated_role.deleted_at is None


class TestDeleteRoleService(_TestRoleBaseService):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = RoleFactory(deleted_at=None)

    def test_delete_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        self.role.deleted_at = datetime.now(UTC)
        mock_role_repo.delete.return_value = self.role
        role_service = RoleService(mock_role_repo)

        role = role_service.delete(self.role.id)

        mock_role_repo.delete.assert_called_once_with(self.role.id)
        assert isinstance(role, Role)
        assert role.id == self.role.id
        assert role.deleted_at == self.role.deleted_at
