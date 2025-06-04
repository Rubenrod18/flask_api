from datetime import datetime

from app.database.factories.role_factory import RoleFactory
from app.extensions import db
from app.models import Role
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
        self.assertIsNone(db.session.query(Role).filter_by(name=role_data['name']).one_or_none())

    def test_find_role(self):
        role = RoleFactory(deleted_at=None)

        test_cases = [
            ('id', (), {'id': role.id}),
            ('name', (), {'name': role.name}),
            ('description', (), {'description': role.description}),
            ('label', (), {'label': role.label}),
            ('created_at', (), {'created_at': role.created_at}),
            ('updated_at', (), {'updated_at': role.updated_at}),
            ('deleted_at', (), {'deleted_at': None}),
            ('id', (Role.id == role.id,), {}),
            ('name', (Role.name == role.name,), {}),
            ('description', (Role.description == role.description,), {}),
            ('label', (Role.label == role.label,), {}),
            ('created_at', (Role.created_at == role.created_at,), {}),
            ('updated_at', (Role.updated_at == role.updated_at,), {}),
            ('deleted_at', (Role.deleted_at.is_(None),), {}),
        ]

        for description, args, kwargs in test_cases:
            with self.subTest():
                result = self.repository.find(*args, **kwargs)
                self.assertIsNotNone(result, (description, args, kwargs))
                self.assertTrue(isinstance(result, Role), (description, args, kwargs))
                self.assertEqual(result.id, role.id, (description, args, kwargs))

    def test_delete_soft_role(self):
        role = RoleFactory()

        role = self.repository.delete(role.id)

        self.assertTrue(isinstance(role.deleted_at, datetime))
        self.assertIsNone(db.session.query(Role).filter_by(name=role.name, deleted_at=role.deleted_at).one_or_none())

    def test_delete_hard_role(self):
        role = RoleFactory()

        with self.assertRaises(NotImplementedError):
            self.repository.delete(role.id, force_delete=True)
