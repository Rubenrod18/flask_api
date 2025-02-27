from datetime import datetime, UTC
from unittest.mock import MagicMock

from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, NotFound

from app.database.factories.user_factory import UserFactory
from app.managers import UserManager
from app.models import Role, User
from app.serializers import UserExportWordSerializer, UserSerializer
from tests.base.base_test import TestBase


class TestUserSerializer(TestBase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory(
            name='Test',
            last_name='User',
            email='test@example.com',
            password='securepassword123',
            genre='m',
            birth_date='1990-01-01',
            active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
        )
        self.user_manager = MagicMock(spec=UserManager)
        self.user_manager.find_by_email.return_value = None
        self.user_manager.model = MagicMock(spec=User)
        self.user_manager.model.deleted_at.is_.return_value = None

        self.serializer = UserSerializer()
        self.serializer._user_manager = self.user_manager

    def test_valid_serialization(self):
        serialized_data = self.serializer.dump(self.user)

        self.assertEqual(serialized_data['id'], self.user.id)
        self.assertEqual(serialized_data['email'], self.user.email)
        self.assertIn('roles', serialized_data)
        self.assertEqual(len(serialized_data['roles']), 1)
        self.assertEqual(serialized_data['roles'][0]['name'], self.user.roles[0].name)

    def test_valid_email_validation(self):
        self.user_manager.find_by_email.return_value = None

        self.serializer.load({'email': 'new_email@example.com'}, partial=True)

    def test_invalid_email_validation(self):
        self.user_manager.find_by_email.return_value = self.user

        with self.assertRaises(BadRequest) as context:
            self.serializer.load({'email': self.user.email}, partial=True)

        self.assertEqual(context.exception.code, 400)
        self.assertEqual(context.exception.description, 'User email already created')

    def test_validate_existing_user_id(self):
        self.user_manager.find.return_value = self.user
        self.user_manager.find.return_value = self.user

        self.serializer.load({'id': 1}, partial=True)

    def test_validate_nonexistent_user_id(self):
        self.user_manager.find.return_value = None

        with self.assertRaises(NotFound) as context:
            self.serializer.validate_id(999)

        self.assertEqual(context.exception.code, 404)
        self.assertEqual(context.exception.description, 'User not found')

    def test_valid_role_id(self):
        self.serializer.load({'role_id': self.user.roles[0].id}, partial=True)

    def test_invalid_role_id(self):
        with self.assertRaises(NotFound) as context:
            self.serializer.load({'role_id': 999}, partial=True)

        self.assertEqual(context.exception.code, 404)
        self.assertEqual(context.exception.description, 'Role not found')

    def test_missing_required_fields(self):
        with self.assertRaises(ValidationError) as context:
            self.serializer.load({'name': 'Test', 'last_name': 'User'})

        self.assertEqual(context.exception.messages, {'email': ['Missing data for required field.']})

    def test_invalid_role_id_format(self):
        with self.assertRaises(NotFound) as context:
            self.serializer.load({'role_id': 'invalid_role'}, partial=True)

        self.assertEqual(context.exception.description, 'Role not found')

    def test_valid_serialization_with_roles(self):
        self.user.roles = [Role(id=1, name='admin', label='Administrator')]
        serialized_data = self.serializer.dump(self.user)
        self.assertEqual(len(serialized_data['roles']), 1)
        self.assertEqual(serialized_data['roles'][0]['name'], 'admin')

    def test_user_export_word_serializer(self):
        serializer = UserExportWordSerializer()

        data = {'to_pdf': 1}
        result = serializer.load(data)
        self.assertEqual(result['to_pdf'], 1)

        with self.assertRaises(ValidationError):
            serializer.load({'to_pdf': 3})

        data = {'to_pdf': '1'}
        result = serializer.load(data)
        self.assertEqual(result['to_pdf'], 1)
