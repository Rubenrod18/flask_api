from datetime import datetime, UTC
from unittest.mock import patch, PropertyMock

from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy.query import Query

from app.database.factories.role_factory import RoleFactory
from app.extensions import db
from app.helpers.sqlalchemy_query_builder import EQUAL_OP
from app.managers import RoleManager
from app.models import Role
from tests.base.base_test import BaseTest


class RoleManagerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.manager = RoleManager()

    def test_check_manager_property(self):
        with patch.object(RoleManager, 'model', new_callable=PropertyMock) as mock_value:
            mock_value.return_value = Role
            role_manager = RoleManager()
            self.assertEqual(type(role_manager.model), DefaultMeta)

    @patch('app.managers.role.RoleRepository.create', autospec=True)
    def test_create_role(self, mock_repo_create):
        role_data = RoleFactory.build_dict()
        mock_repo_create.return_value = Role(**role_data)

        role = self.manager.create(**role_data)

        mock_repo_create.assert_called_once()
        self.assertEqual(role.name, role_data['name'])
        self.assertEqual(role.description, role_data['description'])
        self.assertEqual(role.label, role_data['label'])
        self.assertTrue(db.session.query(Role.id).filter().first() is None)

    @patch('app.managers.role.RoleRepository.find', autospec=True)
    def test_save_role(self, mock_repo_find):
        role = RoleFactory()
        role_data = RoleFactory.build_dict()
        mock_repo_find.return_value = db.session.get(Role, role.id)

        role = self.manager.save(role.id, **role_data)

        mock_repo_find.assert_called_once()
        self.assertEqual(role.name, role_data['name'])
        self.assertEqual(role.description, role_data['description'])
        self.assertEqual(role.label, role_data['label'])
        self.assertTrue(isinstance(role.created_at, datetime))
        self.assertTrue(isinstance(role.updated_at, datetime))
        self.assertIsNone(role.deleted_at)
        self.assertIsNotNone(db.session.get(Role, role.id))
        self.assertTrue(db.session.query(Role.id).filter(Role.id != role.id).first() is None)

    @patch('app.managers.base.SQLAlchemyQueryBuilder.get_request_query_fields', autospec=True)
    @patch('app.managers.base.SQLAlchemyQueryBuilder.create_search_query', autospec=True)
    def test_get_roles_no_filter_criteria(self, mock_create_search_query, mock_get_request_query_fields):
        mock_create_search_query.return_value = db.session.query(Role)
        mock_get_request_query_fields.return_value = 0, 10, []
        RoleFactory.create_batch(5)

        all_roles = self.manager.get()

        mock_get_request_query_fields.assert_called_once()
        mock_create_search_query.assert_called_once()
        self.assertTrue(isinstance(all_roles['query'], Query))
        self.assertTrue(all(isinstance(doc, Role) for doc in all_roles['query']))
        self.assertEqual(all_roles['records_filtered'], 5)
        self.assertEqual(all_roles['records_total'], 5)

    @patch('app.managers.base.SQLAlchemyQueryBuilder.get_request_query_fields', autospec=True)
    @patch('app.managers.base.SQLAlchemyQueryBuilder.create_search_query', autospec=True)
    def test_get_roles_with_filter_criteria(self, mock_create_search_query, mock_get_request_query_fields):
        created_roles = RoleFactory.create_batch(5)
        mock_create_search_query.return_value = db.session.query(Role).where(Role.name == created_roles[0].name)
        mock_get_request_query_fields.return_value = 0, 10, []

        filtered_roles = self.manager.get(
            **{
                'items_per_page': 10,
                'order': [],
                'page_number': 1,
                'search': [
                    {
                        'field_name': 'name',
                        'field_operator': EQUAL_OP,
                        'field_value': created_roles[0].name,
                    }
                ],
            }
        )

        self.assertTrue(isinstance(filtered_roles['query'], Query))
        self.assertTrue(all(isinstance(doc, Role) for doc in filtered_roles['query']))
        self.assertEqual(filtered_roles['records_filtered'], 1)
        self.assertEqual(filtered_roles['records_total'], 5)

    @patch('app.managers.role.RoleRepository.delete', autospec=True)
    def test_delete_soft_role(self, mock_repo_delete):
        role = RoleFactory(deleted_at=None)

        def fake_delete(self, doc, force_delete=False):  # noqa  # pylint: disable=unused-argument
            doc.deleted_at = datetime.now(UTC)
            return doc

        mock_repo_delete.side_effect = fake_delete

        deleted_role = self.manager.delete(role.id)

        mock_repo_delete.assert_called_once()
        self.assertTrue(isinstance(deleted_role.deleted_at, datetime))
        self.assertEqual(deleted_role.id, role.id)
        self.assertTrue(isinstance(deleted_role.deleted_at, datetime))

    @patch('app.managers.role.RoleRepository.find', autospec=True)
    def test_find_by_id_role(self, mock_repo_find):
        role = RoleFactory(deleted_at=None)
        mock_repo_find.return_value = db.session.get(Role, role.id)

        found_role = self.manager.find_by_id(role.id)

        mock_repo_find.assert_called_once()
        self.assertTrue(isinstance(found_role, Role))
        self.assertEqual(found_role.id, role.id)

    @patch('app.managers.role.RoleRepository.find', autospec=True)
    def test_find_by_name_role(self, mock_repo_find):
        role = RoleFactory(deleted_at=None)
        mock_repo_find.return_value = db.session.get(Role, role.id)

        found_role = self.manager.find_by_name(role.name)

        mock_repo_find.assert_called_once()
        self.assertTrue(isinstance(found_role, Role))
        self.assertEqual(found_role.name, role.name)
