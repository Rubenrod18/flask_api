from datetime import datetime, UTC
from unittest.mock import MagicMock

from werkzeug.exceptions import BadRequest, NotFound

from app.database.factories.role_factory import RoleFactory
from app.models import Role
from app.repositories import RoleRepository
from app.serializers import RoleSerializer
from tests.base.base_test import BaseTest


class RoleSerializerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.role = RoleFactory(
            name='admin',
            description='Administrator role',
            label='Administrator',
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        self.role_repository = MagicMock(spec=RoleRepository)
        self.role_repository.find_by_id.return_value = self.role
        self.role_repository.model = MagicMock(spec=Role)
        self.role_repository.model.deleted_at.is_.return_value = None

        self.serializer = RoleSerializer()
        self.serializer._role_repository = self.role_repository  # pylint: disable=protected-access

    def test_valid_serialization(self):
        serialized_data = self.serializer.dump(self.role)

        self.assertEqual(serialized_data['id'], self.role.id)
        self.assertEqual(serialized_data['name'], self.role.name)
        self.assertEqual(serialized_data['description'], self.role.description)
        self.assertEqual(serialized_data['label'], self.role.label)

    def test_validate_existing_role_id(self):
        self.serializer.load({'id': 1}, partial=True)

    def test_validate_nonexistent_role_id(self):
        self.role_repository.find_by_id.return_value = None

        with self.assertRaises(NotFound) as context:
            self.serializer.validate_id(999)

        self.assertEqual(context.exception.code, 404)
        self.assertEqual(context.exception.description, 'Role not found')

    def test_validate_deleted_role_id(self):
        self.role.deleted_at = datetime.now(UTC)

        with self.assertRaises(NotFound) as context:
            self.serializer.validate_id(1)

        self.assertEqual(context.exception.description, 'Role not found')

    def test_sluglify_name(self):
        data = {'label': 'New Role'}

        result = self.serializer.load(data, partial=True)

        self.assertEqual(result['name'], 'new-role')

    def test_validate_existing_role_name(self):
        self.role_repository.find_by_name.return_value = self.role

        with self.assertRaises(BadRequest) as context:
            self.serializer.load({'name': 'admin'}, partial=True)

        self.assertEqual(context.exception.description, 'Role name already created')
