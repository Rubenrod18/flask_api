from datetime import datetime, UTC
from unittest import mock
from unittest.mock import MagicMock

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import AdminUserFactory
from app.models import Role
from app.repositories import RoleRepository
from app.services import RoleService
from tests.base.base_test import BaseTest


class _RoleBaseServiceTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.admin_user = AdminUserFactory(deleted_at=None)


class CreateRoleServiceTest(_RoleBaseServiceTest):
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
        self.assertTrue(isinstance(created_role, Role))
        self.assertEqual(created_role.name, role.name)
        self.assertEqual(created_role.description, role.description)
        self.assertEqual(created_role.label, role.label)
        self.assertTrue(created_role.created_at)
        self.assertEqual(created_role.updated_at, created_role.created_at)
        self.assertIsNone(created_role.deleted_at)


class FindByIdRoleServiceTest(_RoleBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.role = RoleFactory(deleted_at=None)

    def test_find_by_id_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        mock_role_repo.find_by_id.return_value = self.role
        role_service = RoleService(mock_role_repo)

        role = role_service.find_by_id(self.role.id)

        mock_role_repo.find_by_id.assert_called_once_with(self.role.id)
        self.assertTrue(isinstance(role, Role))
        self.assertEqual(role.id, self.role.id)


class GetRoleServiceTest(_RoleBaseServiceTest):
    def setUp(self):
        super().setUp()
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
        self.assertEqual(len(roles), 1)
        self.assertTrue(isinstance(roles[0], Role))
        self.assertEqual(roles[0].id, self.role.id)


class SaveRoleServiceTest(_RoleBaseServiceTest):
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
        self.assertTrue(isinstance(updated_role, Role))
        self.assertEqual(updated_role.name, role.name)
        self.assertEqual(updated_role.description, role.description)
        self.assertEqual(updated_role.label, role.label)
        self.assertTrue(updated_role.created_at)
        self.assertEqual(updated_role.updated_at, updated_role.created_at)
        self.assertIsNone(updated_role.deleted_at)


class DeleteRoleServiceTest(_RoleBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.role = RoleFactory(deleted_at=None)

    def test_delete_role(self):
        mock_role_repo = MagicMock(spec=RoleRepository)
        self.role.deleted_at = datetime.now(UTC)
        mock_role_repo.delete.return_value = self.role
        role_service = RoleService(mock_role_repo)

        role = role_service.delete(self.role.id)

        mock_role_repo.delete.assert_called_once_with(self.role.id)
        self.assertTrue(isinstance(role, Role))
        self.assertEqual(role.id, self.role.id)
        self.assertEqual(role.deleted_at, self.role.deleted_at)


class AssignRoleToUserRoleServiceTest(_RoleBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.role = RoleFactory(deleted_at=None)

    @mock.patch('app.services.role.user_datastore.remove_role_from_user', autospec=True)
    @mock.patch('app.services.role.user_datastore.add_role_to_user', autospec=True)
    @mock.patch('app.services.role.db.session', autospec=True)
    def test_assign_role_to_user_role(self, mock_session, mock_add_role_to_user, mock_remove_role_from_user):
        mock_role_repo = MagicMock(spec=RoleRepository)
        mock_role_repo.find_by_id.return_value = self.role
        role_service = RoleService(mock_role_repo)

        role_service.assign_role_to_user(user=self.admin_user, role_id=self.role.id)

        mock_role_repo.find_by_id.assert_called_once_with(self.role.id)
        mock_remove_role_from_user.assert_called_once_with(self.admin_user, self.admin_user.roles[0])
        mock_add_role_to_user.assert_called_once_with(self.admin_user, self.role)
        mock_session.add.assert_called_once_with(self.admin_user)
        mock_session.flush.assert_called_once_with()
