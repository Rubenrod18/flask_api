# pylint: disable=attribute-defined-outside-init, unused-argument
from datetime import datetime, UTC
from types import SimpleNamespace
from unittest import mock
from unittest.mock import MagicMock

import pytest

from app.repositories import RoleRepository
from app.services import RoleService
from tests.base.base_unit_test import TestBaseUnit


class _TestRoleBaseService(TestBaseUnit):
    @pytest.fixture(autouse=True)
    def base_setup(self, faker):
        self.role_id = faker.random_int()
        self.role = MagicMock(SimpleNamespace, autospec=True)


class TestCreateRoleService(_TestRoleBaseService):
    @mock.patch('app.services.role.db.session')
    def test_create_role(self, mock_session):
        mock_role_repo = MagicMock(spec=RoleRepository)
        mock_role_repo.create.return_value = self.role
        role_service = RoleService(mock_role_repo)
        role_data = {'label': self.faker.name(), 'description': self.faker.sentence()}

        created_role = role_service.create(**role_data)

        mock_role_repo.create.assert_called_once_with(**role_data)
        mock_session.add.assert_called_once_with(self.role)
        mock_session.flush.assert_called_once_with()
        assert isinstance(created_role, SimpleNamespace)


class TestFindByIdRoleService(_TestRoleBaseService):
    def test_find_by_id_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        mock_role_repo.find_by_id.return_value = self.role
        role_service = RoleService(mock_role_repo)

        role = role_service.find_by_id(self.role_id)

        mock_role_repo.find_by_id.assert_called_once_with(self.role_id)
        assert isinstance(role, SimpleNamespace)


class TestGetRoleService(_TestRoleBaseService):
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
        assert isinstance(roles[0], SimpleNamespace)


class TestSaveRoleService(_TestRoleBaseService):
    def test_save_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        mock_role_repo.save.return_value = self.role
        role_service = RoleService(mock_role_repo)
        role_data = {'label': self.faker.name(), 'description': self.faker.sentence()}

        updated_role = role_service.save(self.role_id, **role_data)

        mock_role_repo.save.assert_called_once_with(
            self.role_id,
            **role_data,
        )
        assert isinstance(updated_role, SimpleNamespace)


class TestDeleteRoleService(_TestRoleBaseService):
    def test_delete_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        self.role.deleted_at = datetime.now(UTC)
        mock_role_repo.delete.return_value = self.role
        role_service = RoleService(mock_role_repo)

        role = role_service.delete(self.role_id)

        mock_role_repo.delete.assert_called_once_with(self.role_id)
        assert isinstance(role, SimpleNamespace)
