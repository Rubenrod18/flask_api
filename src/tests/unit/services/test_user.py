from datetime import datetime, UTC
from unittest import mock
from unittest.mock import MagicMock

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.models import User
from app.repositories import UserRepository
from app.services import RoleService, UserService
from tests.base.base_test import BaseTest


class _UserBaseServiceTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.role = RoleFactory(deleted_at=None)
        self.user = UserFactory(deleted_at=None, roles=[self.role])


class CreateUserServiceTest(_UserBaseServiceTest):
    @mock.patch('app.services.user.current_user', autospec=True)
    @mock.patch('app.services.user.user_datastore.create_user', autospec=True)
    @mock.patch('app.services.user.db.session', autospec=True)
    def test_create_user(self, mock_session, mock_create_user, mock_current_user):
        mock_current_user.id = self.user.id
        mock_create_user.return_value = self.user

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.get_last_record.return_value = self.user
        mock_role_service = MagicMock(spec=RoleService)
        mock_role_service.assign_role_to_user.return_value = None
        user_service = UserService(mock_user_repo, mock_role_service)

        user_data = UserFactory.build_dict(exclude={'roles', 'created_by'})
        user_data['role_id'] = self.role.id

        created_user = user_service.create(**user_data)
        user_data.pop('role_id')
        user_data['created_by'] = 1
        user_data['fs_uniquifier'] = 2

        mock_user_repo.get_last_record.assert_called_once()
        mock_create_user.assert_called_once_with(**user_data)
        mock_session.add.assert_called_once_with(self.user)
        mock_session.flush.assert_called_once_with()
        mock_role_service.assign_role_to_user.assert_called_once_with(self.user, self.role.id)
        self.assertTrue(isinstance(created_user, User))
        self.assertEqual(created_user.created_by, self.user.created_by)
        self.assertEqual(created_user.fs_uniquifier, self.user.fs_uniquifier)
        self.assertEqual(created_user.name, self.user.name)
        self.assertEqual(created_user.last_name, self.user.last_name)
        self.assertEqual(created_user.email, self.user.email)
        self.assertEqual(created_user.genre, self.user.genre)
        self.assertEqual(created_user.birth_date, self.user.birth_date)
        self.assertEqual(created_user.active, self.user.active)
        self.assertTrue(created_user.created_at)
        self.assertEqual(created_user.updated_at, created_user.created_at)
        self.assertIsNone(created_user.deleted_at)


class FindByIdUserServiceTest(_UserBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(deleted_at=None, roles=[self.role])

    def test_find_by_id_user(self):
        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.find_by_id.return_value = self.user
        user_service = UserService(mock_user_repo)

        user = user_service.find_by_id(self.user.id)

        mock_user_repo.find_by_id.assert_called_once_with(self.user.id)
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.id, self.user.id)


class GetUserServiceTest(_UserBaseServiceTest):
    def setUp(self):
        super().setUp()
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
        self.assertEqual(len(users), 1)
        self.assertTrue(isinstance(users[0], User))
        self.assertEqual(users[0].id, self.user.id)


class SaveUserServiceTest(_UserBaseServiceTest):
    @mock.patch('app.services.user.db.session', autospec=True)
    @mock.patch('app.services.user.User.reload', autospec=True)
    def test_save_user(self, mock_user_reload, mock_session):
        mock_user_reload.return_value = self.user

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.save.return_value = self.user
        mock_role_service = MagicMock(spec=RoleService)
        mock_role_service.assign_role_to_user.return_value = None
        user_service = UserService(mock_user_repo, mock_role_service)

        user_data = UserFactory.build_dict(exclude={'roles', 'created_by'})
        user_data['role_id'] = self.role.id

        updated_user = user_service.save(self.user.id, **user_data)

        mock_user_repo.save.assert_called_once_with(
            self.user.id,
            **user_data,
        )
        mock_session.flush.assert_called_once_with()
        mock_role_service.assign_role_to_user.assert_called_once_with(self.user, self.role.id)
        mock_user_reload.assert_called_once()
        self.assertTrue(isinstance(updated_user, User))
        self.assertEqual(updated_user.created_by, self.user.created_by)
        self.assertEqual(updated_user.fs_uniquifier, self.user.fs_uniquifier)
        self.assertEqual(updated_user.name, self.user.name)
        self.assertEqual(updated_user.last_name, self.user.last_name)
        self.assertEqual(updated_user.email, self.user.email)
        self.assertEqual(updated_user.genre, self.user.genre)
        self.assertEqual(updated_user.birth_date, self.user.birth_date)
        self.assertEqual(updated_user.active, self.user.active)
        self.assertTrue(updated_user.created_at)
        self.assertEqual(updated_user.updated_at, updated_user.created_at)
        self.assertIsNone(updated_user.deleted_at)

    @mock.patch('app.services.user.db.session', autospec=True)
    @mock.patch('app.services.user.User.reload', autospec=True)
    def test_save_user_no_role_id(self, mock_user_reload, mock_session):
        mock_user_reload.return_value = self.user

        mock_user_repo = MagicMock(spec=UserRepository)
        mock_user_repo.save.return_value = self.user
        mock_role_service = MagicMock(spec=RoleService)
        user_service = UserService(mock_user_repo, mock_role_service)

        user_data = UserFactory.build_dict(exclude={'roles', 'created_by'})

        updated_user = user_service.save(self.user.id, **user_data)

        mock_user_repo.save.assert_called_once_with(
            self.user.id,
            **user_data,
        )
        mock_session.flush.assert_called_once_with()
        mock_role_service.assert_not_called()
        mock_user_reload.assert_called_once()
        self.assertTrue(isinstance(updated_user, User))
        self.assertEqual(updated_user.created_by, self.user.created_by)
        self.assertEqual(updated_user.fs_uniquifier, self.user.fs_uniquifier)
        self.assertEqual(updated_user.name, self.user.name)
        self.assertEqual(updated_user.last_name, self.user.last_name)
        self.assertEqual(updated_user.email, self.user.email)
        self.assertEqual(updated_user.genre, self.user.genre)
        self.assertEqual(updated_user.birth_date, self.user.birth_date)
        self.assertEqual(updated_user.active, self.user.active)
        self.assertTrue(updated_user.created_at)
        self.assertEqual(updated_user.updated_at, updated_user.created_at)
        self.assertIsNone(updated_user.deleted_at)


class DeleteUserServiceTest(_UserBaseServiceTest):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(deleted_at=None, roles=[self.role])

    def test_delete_user(self):
        mock_user_repo = MagicMock(spec=UserRepository)
        self.user.deleted_at = datetime.now(UTC)
        mock_user_repo.delete.return_value = self.user
        user_service = UserService(mock_user_repo)

        user = user_service.delete(self.user.id)

        mock_user_repo.delete.assert_called_once_with(self.user.id)
        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.deleted_at, self.user.deleted_at)
