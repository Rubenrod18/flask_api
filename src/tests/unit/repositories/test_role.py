from datetime import datetime

from app.database.factories.role_factory import RoleFactory
from app.repositories.role import RoleRepository
from tests.base.base_test import BaseTest


class RoleRepositoryTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.repository = RoleRepository()

    def test_create_role(self):
        role_data = RoleFactory.build_dict()

        role = self.repository.create(**role_data)

        self.assertEqual(role.name, role_data['name'])
        self.assertEqual(role.description, role_data['description'])
        self.assertEqual(role.label, role_data['label'])

    def test_find_role(self):
        role = RoleFactory()

        test_cases = [
            ('name', role.name),
            ('description', role.description),
            ('label', role.label),
        ]

        for field_name, field_value in test_cases:
            with self.subTest(msg=field_name, field_value=field_value):
                self.assertTrue(self.repository.find(**{field_name: field_value}))

    def test_delete_soft_role(self):
        role = RoleFactory()

        role = self.repository.delete(role)

        self.assertTrue(isinstance(role.deleted_at, datetime))

    def test_delete_hard_role(self):
        role = RoleFactory()

        with self.assertRaises(NotImplementedError):
            self.repository.delete(role, force_delete=True)
