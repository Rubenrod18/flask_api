from datetime import datetime

import pytest

from app.database.factories.role_factory import RoleFactory
from app.extensions import db
from app.models import Role
from app.repositories.role import RoleRepository


# pylint: disable=attribute-defined-outside-init, unused-argument
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

    @pytest.mark.parametrize(
        'description,args,kwargs',
        [
            ('id', (), lambda r: {'id': r.id}),
            ('name', (), lambda r: {'name': r.name}),
            ('description', (), lambda r: {'description': r.description}),
            ('label', (), lambda r: {'label': r.label}),
            ('created_at', (), lambda r: {'created_at': r.created_at}),
            ('updated_at', (), lambda r: {'updated_at': r.updated_at}),
            ('deleted_at', (), lambda r: {'deleted_at': None}),
            ('id_expr', lambda r: (Role.id == r.id,), lambda r: {}),
            ('name_expr', lambda r: (Role.name == r.name,), lambda r: {}),
            ('description_expr', lambda r: (Role.description == r.description,), lambda r: {}),
            ('label_expr', lambda r: (Role.label == r.label,), lambda r: {}),
            ('created_at_expr', lambda r: (Role.created_at == r.created_at,), lambda r: {}),
            ('updated_at_expr', lambda r: (Role.updated_at == r.updated_at,), lambda r: {}),
            ('deleted_at_expr', lambda r: (Role.deleted_at.is_(None),), lambda r: {}),
        ],
    )
    def test_find_role(self, description, args, kwargs):
        role = RoleFactory(deleted_at=None)
        _args = args(role) if callable(args) else args
        _kwargs = kwargs(role) if callable(kwargs) else kwargs

        result = self.repository.find(*_args, **_kwargs)

        assert result is not None, (description, _args, _kwargs)
        assert isinstance(result, Role), (description, _args, _kwargs)
        assert result.id == role.id, (description, _args, _kwargs)

    @pytest.mark.parametrize(
        'description,args_fn',
        [
            ('description', lambda r: (Role.description == r.description,)),
            ('label', lambda r: (Role.label == r.label,)),
            ('created_at', lambda r: (Role.created_at == r.created_at,)),
            ('updated_at', lambda r: (Role.updated_at == r.updated_at,)),
            ('deleted_at', lambda r: (Role.deleted_at.is_(None),)),
        ],
    )
    def test_find_by_name_role(self, description, args_fn):
        role = RoleFactory(deleted_at=None)
        args = args_fn(role)

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
