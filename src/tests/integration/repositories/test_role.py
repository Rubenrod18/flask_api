from datetime import datetime

import pytest

from app.database.factories.role_factory import RoleFactory
from app.extensions import db
from app.models import Role
from app.repositories.role import RoleRepository


class TestRoleRepository:
    @pytest.fixture(autouse=True)
    def setup(self, app):
        self.repository = RoleRepository()

    def test_create_role(self):
        role_data = RoleFactory.build_dict()

        role = self.repository.create(**role_data)

        assert role.name == role_data['name']
        assert role.description == role_data['description']
        assert role.label == role_data['label']
        assert db.session.query(Role).filter_by(name=role_data['name']).one_or_none() is None

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
            result = self.repository.find(*args, **kwargs)
            assert result is not None, (description, args, kwargs)
            assert isinstance(result, Role), (description, args, kwargs)
            assert result.id == role.id, (description, args, kwargs)

    def test_find_by_name_role(self):
        role = RoleFactory(deleted_at=None)

        test_cases = [
            ('description', (Role.description == role.description,)),
            ('label', (Role.label == role.label,)),
            ('created_at', (Role.created_at == role.created_at,)),
            ('updated_at', (Role.updated_at == role.updated_at,)),
            ('deleted_at', (Role.deleted_at.is_(None),)),
        ]

        for description, args in test_cases:
            result = self.repository.find_by_name(role.name, *args)
            assert result is not None, (description, args)
            assert isinstance(result, Role), (description, args)
            assert result.id == role.id, (description, args)

    def test_find_by_name_not_found_role(self):
        RoleFactory(deleted_at=None)

        found_role = self.repository.find_by_name('fake-role')

        assert found_role is None

    def test_delete_soft_role(self):
        role = RoleFactory()

        role = self.repository.delete(role.id)

        assert isinstance(role.deleted_at, datetime)
        assert db.session.query(Role).filter_by(name=role.name, deleted_at=role.deleted_at).one_or_none() is None

    def test_delete_hard_role(self):
        role = RoleFactory()

        with pytest.raises(NotImplementedError):
            self.repository.delete(role.id, force_delete=True)
