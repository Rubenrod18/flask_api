from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound

from app.models import Role, User
from app.repositories import UserRepository
from app.serializers import UserExportWordSerializer, UserSerializer
from app.serializers.user import VerifyRoleId
from tests.base.base_unit_test import TestBaseUnit


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestUserSerializer(TestBaseUnit):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.user = SimpleNamespace(id=self.faker.random_int(), email=self.faker.email())

        self.user_repository = MagicMock(spec=UserRepository)
        self.user_repository.find_by_id.return_value = None
        self.user_repository.find_by_email.return_value = None
        self.user_repository.model = MagicMock(spec=User)
        self.user_repository.model.deleted_at.is_.return_value = None

        self.serializer = UserSerializer()
        self.serializer._user_repository = self.user_repository  # pylint: disable=protected-access

    def test_valid_serialization(self):
        serialized_data = self.serializer.dump(self.user)

        assert serialized_data == {'id': self.user.id, 'email': self.user.email}

    def test_valid_email_validation(self):
        self.user_repository.find_by_email.return_value = None
        new_email = self.faker.email()

        self.serializer.load({'email': new_email}, partial=True)

        self.user_repository.find_by_email.assert_called_once_with(new_email)

    def test_invalid_email_validation(self):
        self.user_repository.find_by_email.return_value = self.user

        with pytest.raises(ValidationError) as exc_info:
            self.serializer.load({'email': self.user.email}, partial=True)

        self.user_repository.find_by_email.assert_called_once_with(self.user.email)
        assert exc_info.value.messages == {'email': ['User email already created']}

    def test_validate_existing_user_id(self):
        self.user.deleted_at = None
        self.user_repository.find_by_id.return_value = self.user

        self.serializer.load({'id': self.user.id}, partial=True)

        self.user_repository.find_by_id.assert_called_once_with(self.user.id, None)

    def test_validate_nonexistent_user_id(self):
        self.user_repository.find_by_id.return_value = None
        fake_user_id = self.faker.random_int()

        with pytest.raises(NotFound) as exc_info:
            self.serializer.validate_id(fake_user_id)

        self.user_repository.find_by_id.assert_called_once_with(fake_user_id, None)
        assert exc_info.value.code == 404
        assert exc_info.value.description == 'User not found'

    @patch.object(VerifyRoleId, '_deserialize', autospec=True)
    def test_valid_role_id(self, mock_deserialize):
        mock_deserialize.return_value = True

        self.serializer.load({'role_id': self.faker.random_int()}, partial=True)

        mock_deserialize.assert_called_once()

    @patch.object(VerifyRoleId, '_deserialize', autospec=True)
    def test_invalid_role_id(self, mock_deserialize):
        mock_deserialize.side_effect = NotFound('Role not found')

        with pytest.raises(NotFound) as exc_info:
            self.serializer.load({'role_id': 999}, partial=True)

        assert exc_info.value.code == 404
        assert exc_info.value.description == 'Role not found'

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            self.serializer.load({})

        assert exc_info.value.messages == {
            'name': ['Missing data for required field.'],
            'last_name': ['Missing data for required field.'],
            'email': ['Missing data for required field.'],
            'password': ['Missing data for required field.'],
            'birth_date': ['Missing data for required field.'],
        }

    @patch.object(VerifyRoleId, '_deserialize', autospec=True)
    def test_invalid_role_id_format(self, mock_deserialize):
        mock_deserialize.side_effect = NotFound('Role not found')

        with pytest.raises(NotFound) as exc_info:
            self.serializer.load({'role_id': 'invalid_role'}, partial=True)

        assert exc_info.value.description == 'Role not found'

    def test_valid_serialization_with_roles(self):
        self.user.roles = [Role(id=1, name='admin', label='Administrator')]

        serialized_data = self.serializer.dump(self.user)

        assert len(serialized_data['roles']) == 1
        assert serialized_data['roles'][0]['name'] == 'admin'

    def test_user_export_word_serializer(self):
        serializer = UserExportWordSerializer()

        result = serializer.load({'to_pdf': 1})
        assert result['to_pdf'] == 1

        with pytest.raises(ValidationError):
            serializer.load({'to_pdf': 3})

        result = serializer.load({'to_pdf': '1'})
        assert result['to_pdf'] == 1
