from datetime import datetime, UTC
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from marshmallow import ValidationError
from werkzeug.exceptions import NotFound

from app.models import Role
from app.models.role import ROLE_NAME_DELIMITER
from app.repositories import RoleRepository
from app.serializers import RoleSerializer
from tests.base.base_unit_test import TestBaseUnit


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestRoleSerializer(TestBaseUnit):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.role = SimpleNamespace(id=self.faker.random_int(), name=self.faker.word(), deleted_at=None)
        self.role_repository = MagicMock(spec=RoleRepository)
        self.role_repository.find_by_id.return_value = self.role
        self.role_repository.model = MagicMock(spec=Role)
        self.role_repository.model.deleted_at.is_.return_value = None

        self.serializer = RoleSerializer()
        self.serializer._role_repository = self.role_repository  # pylint: disable=protected-access

    def test_valid_serialization(self):
        serialized_data = self.serializer.dump(self.role)

        assert serialized_data == {'id': self.role.id, 'name': self.role.name, 'deleted_at': None}

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
        self.role_repository.find_by_name.return_value = None
        data = {'label': 'New Role'}

        result = self.serializer.load(data, partial=True)

        assert result['name'] == f'new{ROLE_NAME_DELIMITER}role'

    def test_validate_existing_role_name(self):
        self.role_repository.find_by_name.return_value = self.role

        with pytest.raises(ValidationError) as exc_info:
            self.serializer.load({'name': 'admin'}, partial=True)

        assert exc_info.value.messages == {'name': ['Role name already created']}
