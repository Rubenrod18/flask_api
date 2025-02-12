"""Module for testing roles blueprint."""
from sqlalchemy import func

from app.extensions import db
from app.models.role import Role as RoleModel
from app.database.factories.role_factory import RoleFactory
from tests.base.base_api_test import TestBaseApi


class TestRoleEndpoints(TestBaseApi):
    def setUp(self):
        super(TestRoleEndpoints, self).setUp()
        self.base_path = f'{self.base_path}/roles'
        self.role = RoleFactory(deleted_at=None)

    def test_save_role_endpoint(self):
        ignore_fields = {'id', 'created_at', 'updated_at', 'deleted_at', 'name'}
        data = RoleFactory.build_dict(exclude=ignore_fields)
    
        response = self.client.post(f'{self.base_path}', json=data, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')
    
        assert 201 == response.status_code
        assert data.get('label') == json_data.get('label')
        assert data.get('label').lower().replace(' ', '-') == json_data.get('name')
        assert json_data.get('created_at')
        assert json_data.get('updated_at') == json_data.get('created_at')
        assert json_data.get('deleted_at') is None
        
    def test_update_role_endpoint(self):
        role_id = (
            db.session.query(RoleModel.id)
            .filter(RoleModel.deleted_at.is_(None))
            .order_by(func.random())
            .limit(1)
            .scalar()
        )
    
        ignore_fields = {'id', 'created_at', 'updated_at', 'deleted_at', 'name'}
        data = RoleFactory.build_dict(exclude=ignore_fields)
    
        response = self.client.put(f'{self.base_path}/{role_id}', json=data, headers=self.build_headers())
    
        json_response = response.get_json()
        json_data = json_response.get('data')
    
        assert 200 == response.status_code
        assert role_id == json_data.get('id')
        assert data.get('label') == json_data.get('label')
        assert data.get('label').lower().replace(' ', '-') == json_data.get('name')
        assert json_data.get('created_at')
        assert json_data.get('updated_at') >= json_data.get('created_at')
        assert json_data.get('deleted_at') is None
    
    def test_get_role_endpoint(self):
        role_id = (
            db.session.query(RoleModel.id)
            .filter(RoleModel.deleted_at.is_(None))
            .order_by(func.random())
            .limit(1)
            .scalar()
        )
    
        role = db.session.query(RoleModel).filter(RoleModel.id == role_id).one_or_none()
    
        response = self.client.get(f'{self.base_path}/{role_id}', json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')
    
        assert 200 == response.status_code
        assert role_id == json_data.get('id')
        assert role.name == json_data.get('name')
        assert role.name.lower() == json_data.get('name').lower().replace('-', ' ')
        assert role.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
        assert role.updated_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('updated_at')
        assert role.deleted_at == json_data.get('deleted_at')
    
    def test_delete_role_endpoint(self):
        response = self.client.delete(f'{self.base_path}/{self.role.id}', json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')
    
        assert 200 == response.status_code
        assert self.role.id == json_data.get('id')
        assert json_data.get('deleted_at') is not None
        assert json_data.get('deleted_at') >= json_data.get('updated_at')
    
    def test_search_roles_endpoint(self):
        json_body = {
            'search': [
                {
                    'field_name': 'name',
                    'field_operator': 'eq',
                    'field_value': self.role.name,
                },
            ],
            'order': [
                {
                    'field_name': 'name',
                    'sorting': 'desc',
                },
            ],
        }
    
        response = self.client.post(f'{self.base_path}/search', json=json_body, headers=self.build_headers())
        json_response = response.get_json()
    
        role_data = json_response.get('data')
        records_total = json_response.get('records_total')
        records_filtered = json_response.get('records_filtered')
    
        assert 200 == response.status_code
        assert isinstance(role_data, list)
        assert records_total > 0
        assert 0 < records_filtered <= records_total
        assert role_data[0]['name'].find(self.role.name) != -1
