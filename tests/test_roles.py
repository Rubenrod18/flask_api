from datetime import datetime

from flask.testing import FlaskClient
from peewee import fn
from playhouse.shortcuts import model_to_dict

from app.extensions import db_wrapper
from app.models.role import Role as RoleModel


def test_save_role_endpoint(client: FlaskClient):
    role = RoleModel.fake()

    data = model_to_dict(role)
    del data['id']
    del data['slug']
    del data['created_at']
    del data['updated_at']
    del data['deleted_at']

    response = client.post('/roles', json=data)

    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 201 == response.status_code
    assert data.get('name') == json_data.get('name')
    assert data.get('name').lower() == json_data.get('name').lower().replace('-', ' ')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') == json_data.get('created_at')
    assert json_data.get('deleted_at') is None


def test_get_role_endpoint(client: FlaskClient):
    role_id = (RoleModel.select(RoleModel.id)
               .where(RoleModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)

    role = RoleModel.get(RoleModel.id == role_id)

    db_wrapper.database.close()

    response = client.get('/roles/%s' % role_id)

    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert role.name == json_data.get('name')
    assert role.name.lower() == json_data.get('name').lower().replace('-', ' ')
    assert datetime.timestamp(role.created_at) == json_data.get('created_at')
    assert datetime.timestamp(role.updated_at) == json_data.get('updated_at')
    assert role.deleted_at == json_data.get('deleted_at')


def test_update_role_endpoint(client: FlaskClient):
    role_id = (RoleModel.select(RoleModel.id)
               .where(RoleModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)
    db_wrapper.database.close()

    role = RoleModel.fake()

    data = model_to_dict(role)
    del data['id']
    del data['slug']
    del data['created_at']
    del data['updated_at']
    del data['deleted_at']

    response = client.put('/roles/%s' % role_id, json=data)

    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert data.get('name') == json_data.get('name')
    assert role.name.lower() == json_data.get('name').lower().replace('-', ' ')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') >= json_data.get('created_at')
    assert json_data.get('deleted_at') is None


def test_delete_role_endpoint(client: FlaskClient):
    role_id = (RoleModel.select(RoleModel.id)
               .where(RoleModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)
    db_wrapper.database.close()

    response = client.delete('/roles/%s' % role_id)

    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert role_id == json_data.get('id')
    assert json_data.get('deleted_at') is not None
    assert json_data.get('deleted_at') >= json_data.get('updated_at')


def test_search_roles_endpoint():
    pass
