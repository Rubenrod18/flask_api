from datetime import datetime, UTC
from random import choice
from unittest.mock import MagicMock

import pytest
from marshmallow import ValidationError
from werkzeug.exceptions import BadRequest, NotFound

from app.database.factories.role_factory import RoleFactory
from app.database.factories.user_factory import UserFactory
from app.models import Role, User
from app.models.user import Genre
from app.repositories import UserRepository
from app.serializers import UserExportWordSerializer, UserSerializer


class TestUserSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, app, faker):
        self.faker = faker
        self.user = UserFactory(
            name=self.faker.name(),
            last_name=self.faker.last_name(),
            email=self.faker.email(),
            password=self.faker.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True),
            genre=choice(Genre.to_list()),
            birth_date='1990-01-01',
            active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            deleted_at=None,
            roles=[RoleFactory(deleted_at=None)],
        )
        self.user_repository = MagicMock(spec=UserRepository)
        self.user_repository.find_by_email.return_value = None
        self.user_repository.model = MagicMock(spec=User)
        self.user_repository.model.deleted_at.is_.return_value = None

        self.serializer = UserSerializer()
        self.serializer._user_repository = self.user_repository  # pylint: disable=protected-access

    def test_valid_serialization(self):
        serialized_data = self.serializer.dump(self.user)

        assert serialized_data['id'] == self.user.id
        assert serialized_data['email'] == self.user.email
        assert 'roles' in serialized_data
        assert len(serialized_data['roles']) == 1
        assert serialized_data['roles'][0]['name'] == self.user.roles[0].name

    def test_valid_email_validation(self):
        self.user_repository.find_by_email.return_value = None

        self.serializer.load({'email': 'new_email@example.com'}, partial=True)

    def test_invalid_email_validation(self):
        self.user_repository.find_by_email.return_value = self.user

        with pytest.raises(BadRequest) as exc_info:
            self.serializer.load({'email': self.user.email}, partial=True)

        assert exc_info.value.code == 400
        assert exc_info.value.description == 'User email already created'

    def test_validate_existing_user_id(self):
        self.user_repository.find_by_id.return_value = self.user
        self.user_repository.find_by_id.return_value = self.user

        self.serializer.load({'id': 1}, partial=True)

    def test_validate_nonexistent_user_id(self):
        self.user_repository.find_by_id.return_value = None

        with pytest.raises(NotFound) as exc_info:
            self.serializer.validate_id(999)

        assert exc_info.value.code == 404
        assert exc_info.value.description == 'User not found'

    def test_valid_role_id(self):
        self.serializer.load({'role_id': self.user.roles[0].id}, partial=True)

    def test_invalid_role_id(self):
        with pytest.raises(NotFound) as exc_info:
            self.serializer.load({'role_id': 999}, partial=True)

        assert exc_info.value.code == 404
        assert exc_info.value.description == 'Role not found'

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            self.serializer.load({})

        assert (
            exc_info.value.messages,
            {
                'name': ['Missing data for required field.'],
                'last_name': ['Missing data for required field.'],
                'email': ['Missing data for required field.'],
                'password': ['Missing data for required field.'],
                'birth_date': ['Missing data for required field.'],
            },
        )

    def test_invalid_role_id_format(self):
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
