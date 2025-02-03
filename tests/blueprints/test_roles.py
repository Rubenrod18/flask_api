"""Module for testing roles blueprint."""
from peewee import fn
from sqlalchemy import func

from app.extensions import db, db_wrapper
from app.models.role import Role as RoleModel
from tests.custom_flask_client import CustomFlaskClient


def test_save_role_endpoint(client: CustomFlaskClient, auth_header: any, factory: any):
    ignore_fields = ['id', 'created_at', 'updated_at', 'deleted_at', 'name']
    data = factory('Role').make(exclude=ignore_fields, to_dict=True)

    response = client.post('/api/roles', json=data, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 201 == response.status_code
    assert data.get('label') == json_data.get('label')
    assert data.get('label').lower().replace(' ', '-') == json_data.get('name')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') == json_data.get('created_at')
    assert json_data.get('deleted_at') is None


def test_update_role_endpoint(client: CustomFlaskClient, auth_header: any, factory: any):
    role_id = (
        db.session.query(RoleModel.id)
        .filter(RoleModel.deleted_at.is_(None))
        .order_by(func.random())
        .limit(1)
        .scalar()
    )

    ignore_fields = ['id', 'created_at', 'updated_at', 'deleted_at', 'name']
    data = factory('Role').make(exclude=ignore_fields, to_dict=True)

    response = client.put('/api/roles/%s' % role_id, json=data, headers=auth_header())

    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert data.get('label') == json_data.get('label')
    assert data.get('label').lower().replace(' ', '-') == json_data.get('name')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') >= json_data.get('created_at')
    assert json_data.get('deleted_at') is None


def test_get_role_endpoint(client: CustomFlaskClient, auth_header: any):
    role_id = (
        db.session.query(RoleModel.id)
        .filter(RoleModel.deleted_at.is_(None))
        .order_by(func.random())
        .limit(1)
        .scalar()
    )

    role = db.session.query(RoleModel).filter(RoleModel.id == role_id).one_or_none()

    response = client.get('/api/roles/%s' % role_id, json={}, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert role.name == json_data.get('name')
    assert role.name.lower() == json_data.get('name').lower().replace('-', ' ')
    assert role.get_created_at().strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
    assert role.get_updated_at().strftime('%Y-%m-%d %H:%M:%S') == json_data.get('updated_at')
    assert role.get_deleted_at() == json_data.get('deleted_at')


def test_delete_role_endpoint(client: CustomFlaskClient, auth_header: any):
    role_id = (
        db.session.query(RoleModel.id)
        .filter(RoleModel.deleted_at.is_(None))
        .order_by(func.random())
        .limit(1)
        .scalar()
    )

    response = client.delete('/api/roles/%s' % role_id, json={}, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert json_data.get('deleted_at') is not None
    assert json_data.get('deleted_at') >= json_data.get('updated_at')


def test_search_roles_endpoint(client: CustomFlaskClient, auth_header: any):
    role_name = (db.session.query(RoleModel.name)
          .filter(RoleModel.deleted_at.is_(None))
          .order_by(func.random())
          .limit(1)
          .scalar())

    json_body = {
        'search': [
            {
                'field_name': 'name',
                'field_operator': 'eq',
                'field_value': role_name,
            },
        ],
        'order': [
            {
                'field_name': 'name',
                'sorting': 'desc',
            },
        ],
    }

    response = client.post('/api/roles/search', json=json_body, headers=auth_header())
    json_response = response.get_json()

    role_data = json_response.get('data')
    records_total = json_response.get('records_total')
    records_filtered = json_response.get('records_filtered')

    assert 200 == response.status_code
    assert isinstance(role_data, list)
    assert records_total > 0
    assert 0 < records_filtered <= records_total
    assert role_data[0]['name'].find(role_name) != -1
