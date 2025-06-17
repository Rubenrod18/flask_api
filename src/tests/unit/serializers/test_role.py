from datetime import datetime, UTC
from unittest.mock import MagicMock

import pytest
from werkzeug.exceptions import BadRequest, NotFound

from app.database.factories.role_factory import RoleFactory
from app.models import Role
from app.repositories import RoleRepository
from app.serializers import RoleSerializer


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestRoleSerializer:
    @pytest.fixture(autouse=True)
    def setup(self, app):
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

        assert serialized_data['id'] == self.role.id
        assert serialized_data['name'] == self.role.name
        assert serialized_data['description'] == self.role.description
        assert serialized_data['label'] == self.role.label

    def test_validate_existing_role_id(self):
        role = self.serializer.load({'id': self.role.id}, partial=True)

        assert role['id'] == self.role.id

    def test_validate_nonexistent_role_id(self):
        self.role_repository.find_by_id.return_value = None

        with pytest.raises(NotFound) as exc_info:
            self.serializer.validate_id(999)

        assert exc_info.value.code == 404
        assert exc_info.value.description == 'Role not found'

    def test_validate_deleted_role_id(self):
        self.role.deleted_at = datetime.now(UTC)

        with pytest.raises(NotFound) as exc_info:
            self.serializer.validate_id(1)

        assert exc_info.value.description == 'Role not found'

    def test_sluglify_name(self):
        data = {'label': 'New Role'}

        result = self.serializer.load(data, partial=True)

        assert result['name'] == 'new-role'

    def test_validate_existing_role_name(self):
        self.role_repository.find_by_name.return_value = self.role

        with pytest.raises(BadRequest) as exc_info:
            self.serializer.load({'name': 'admin'}, partial=True)

        assert exc_info.value.description == 'Role name already created'
