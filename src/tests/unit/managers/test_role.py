from datetime import datetime

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
        self.assertEqual(type(self.manager.model), DefaultMeta)

    def test_create_role(self):
        role_data = RoleFactory.build_dict()

        role = self.manager.create(**role_data)

        self.assertEqual(role.name, role_data['name'])
        self.assertEqual(role.description, role_data['description'])
        self.assertEqual(role.label, role_data['label'])
        self.assertTrue(db.session.query(Role.id).filter().first() is None)

    def test_save_role(self):
        role = RoleFactory()
        role_data = RoleFactory.build_dict()

        role = self.manager.save(role.id, **role_data)

        self.assertEqual(role.name, role_data['name'])
        self.assertEqual(role.description, role_data['description'])
        self.assertEqual(role.label, role_data['label'])
        self.assertIsNotNone(db.session.get(Role, role.id))
        self.assertTrue(db.session.query(Role.id).filter(Role.id != role.id).first() is None)

    def test_get_roles(self):
        created_docs = RoleFactory.create_batch(5)

        all_docs = self.manager.get()

        self.assertTrue(isinstance(all_docs['query'], Query))
        self.assertTrue(all(isinstance(doc, Role) for doc in all_docs['query']))
        self.assertEqual(all_docs['records_filtered'], 5)
        self.assertEqual(all_docs['records_total'], 5)

        filtered_docs = self.manager.get(
            **{
                'items_per_page': 10,
                'order': [],
                'page_number': 1,
                'search': [
                    {
                        'field_name': 'name',
                        'field_operator': EQUAL_OP,
                        'field_value': created_docs[0].name,
                    }
                ],
            }
        )

        self.assertTrue(isinstance(filtered_docs['query'], Query))
        self.assertTrue(all(isinstance(doc, Role) for doc in filtered_docs['query']))
        self.assertEqual(filtered_docs['records_filtered'], 1)
        self.assertEqual(filtered_docs['records_total'], 5)

    def test_delete_soft_role(self):
        role = RoleFactory(deleted_at=None)

        deleted_role = self.manager.delete(role.id)

        self.assertTrue(isinstance(deleted_role.deleted_at, datetime))
        self.assertEqual(deleted_role.id, role.id)
        self.assertTrue(isinstance(deleted_role.deleted_at, datetime))

    def test_find_by_id_role(self):
        role = RoleFactory(deleted_at=None)

        found_role = self.manager.find_by_id(role.id)

        self.assertTrue(isinstance(found_role, Role))
        self.assertEqual(found_role.id, role.id)

    def test_find_by_name_role(self):
        role = RoleFactory(deleted_at=None)

        found_role = self.manager.find_by_name(role.name)

        self.assertTrue(isinstance(found_role, Role))
        self.assertEqual(found_role.id, role.id)
