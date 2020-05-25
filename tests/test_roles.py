from flask.testing import FlaskClient
from peewee import fn

from app.extensions import db_wrapper
from app.models.role import Role as RoleModel


def test_save_role_endpoint(client: FlaskClient, auth_header: any, factory: any):
    ignore_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    data = factory('Role').make(exclude=ignore_fields, to_dict=True)

    response = client.post('/roles', json=data, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 201 == response.status_code
    assert data.get('name') == json_data.get('name')
    assert data.get('name').lower() == json_data.get('name').lower().replace('-', ' ')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') == json_data.get('created_at')
    assert json_data.get('deleted_at') is None


def test_update_role_endpoint(client: FlaskClient, auth_header: any, factory: any):
    role_id = (RoleModel.select(RoleModel.id)
               .where(RoleModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)
    db_wrapper.database.close()

    ignore_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    data = factory('Role').make(exclude=ignore_fields, to_dict=True)

    response = client.put('/roles/%s' % role_id, json=data, headers=auth_header())

    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert data.get('name') == json_data.get('name')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') >= json_data.get('created_at')
    assert json_data.get('deleted_at') is None


def test_get_role_endpoint(client: FlaskClient, auth_header: any):
    role_id = (RoleModel.select(RoleModel.id)
               .where(RoleModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)

    role = RoleModel.get(RoleModel.id == role_id)
    db_wrapper.database.close()

    response = client.get('/roles/%s' % role_id, json={}, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert role.name == json_data.get('name')
    assert role.name.lower() == json_data.get('name').lower().replace('-', ' ')
    assert role.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
    assert role.updated_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('updated_at')
    assert role.deleted_at == json_data.get('deleted_at')


def test_delete_role_endpoint(client: FlaskClient, auth_header: any):
    role_id = (RoleModel.select(RoleModel.id)
               .where(RoleModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)
    db_wrapper.database.close()

    response = client.delete('/roles/%s' % role_id, json={}, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert json_data.get('deleted_at') is not None
    assert json_data.get('deleted_at') >= json_data.get('updated_at')


def test_search_roles_endpoint(client: FlaskClient, auth_header: any):
    role_name = (RoleModel.select(RoleModel.name)
                 .where(RoleModel.deleted_at.is_null())
                 .order_by(fn.Random())
                 .limit(1)
                 .get()
                 .name)
    db_wrapper.database.close()

    json_body = {
        'search': [
            {
                'field_name': 'name',
                'field_value': role_name,
            }
        ],
        'order': 'desc',
        'sort': 'id',
    }

    response = client.post('/roles/search', json=json_body, headers=auth_header())
    json_response = response.get_json()

    role_data = json_response.get('data')
    records_total = json_response.get('records_total')
    records_filtered = json_response.get('records_filtered')

    assert 200 == response.status_code
    assert isinstance(role_data, list)
    assert records_total > 0
    assert records_filtered > 0 and records_filtered <= records_total
    assert role_data[0]['name'].find(role_name) != -1
