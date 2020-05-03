import base64
import binascii
import os

from flask.testing import FlaskClient
from peewee import fn
from playhouse.shortcuts import model_to_dict

from app.extensions import db_wrapper
from app.models.user import User as UserModel
from database.factories import Factory


def test_save_user_endpoint(client: FlaskClient, auth_header: any):
    ignore_fields = [UserModel.id, UserModel.role, UserModel.active, UserModel.created_at, UserModel.updated_at,
                     UserModel.deleted_at]
    user = Factory('User').make()
    role = user.role

    data = model_to_dict(user, exclude=ignore_fields)
    data['role_id'] = role.id
    data['password'] = os.getenv('TEST_USER_PASSWORD')

    response = client.post('/users', json=data, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 201 == response.status_code
    assert data.get('name') == json_data.get('name')
    assert data.get('last_name') == json_data.get('last_name')
    assert data.get('birth_date') == json_data.get('birth_date')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') == json_data.get('created_at')
    assert json_data.get('deleted_at') is None

    assert role.id == json_data.get('role').get('id')
    assert role.name == json_data.get('role').get('name')
    assert role.slug == json_data.get('role').get('slug')
    assert role.created_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('role').get('created_at')
    assert role.updated_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('role').get('updated_at')
    assert role.deleted_at == json_data.get('role').get('deleted_at')


def test_update_user_endpoint(client: FlaskClient, auth_header: any):
    user_id = (UserModel.select(UserModel.id)
               .where(UserModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)

    ignore_fields = [UserModel.id, UserModel.role, UserModel.active, UserModel.created_at, UserModel.updated_at,
                     UserModel.deleted_at]
    user = Factory('User').make()
    role = user.role

    data = model_to_dict(user, exclude=ignore_fields)
    data['role_id'] = role.id
    data['password'] = os.getenv('TEST_USER_PASSWORD')

    response = client.put('/users/%s' % user_id, json=data, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert user_id == json_data.get('id')
    assert data.get('name') == json_data.get('name')
    assert data.get('last_name') == json_data.get('last_name')
    assert data.get('birth_date') == json_data.get('birth_date')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') >= json_data.get('created_at')
    assert json_data.get('deleted_at') is None

    assert role.id == json_data.get('role').get('id')
    assert role.name == json_data.get('role').get('name')
    assert role.slug == json_data.get('role').get('slug')
    assert role.created_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('role').get('created_at')
    assert role.updated_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('role').get('updated_at')
    assert role.deleted_at == json_data.get('role').get('deleted_at')


def test_get_user_endpoint(client: FlaskClient, auth_header: any):
    user_id = (UserModel.select(UserModel.id)
               .where(UserModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)

    user = UserModel.get(UserModel.id == user_id)

    db_wrapper.database.close()

    response = client.get('/users/%s' % user_id, headers=auth_header())

    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert user_id == json_data.get('id')
    assert user.name == json_data.get('name')
    assert user.last_name == json_data.get('last_name')
    assert user.birth_date.strftime('%Y-%m-%d') == json_data.get('birth_date')
    assert user.created_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('created_at')
    assert user.updated_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('updated_at')
    assert user.deleted_at == json_data.get('deleted_at')


def test_delete_user_endpoint(client: FlaskClient, auth_header: any):
    user_id = (UserModel.select(UserModel.id)
               .where(UserModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)
    db_wrapper.database.close()

    response = client.delete('/users/%s' % user_id, headers=auth_header())

    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert user_id == json_data.get('id')
    assert json_data.get('deleted_at') is not None
    assert json_data.get('deleted_at') >= json_data.get('updated_at')


def test_search_users_endpoint(client: FlaskClient, auth_header: any):
    user_name = (UserModel.select(UserModel.name)
               .where(UserModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .name)
    db_wrapper.database.close()

    json_body = {
        'search': [
            {
                'field_name': 'name',
                'field_value': user_name,
            }
        ],
        'order': 'desc',
        'sort': 'id',
    }

    response = client.post('/users/search', json=json_body, headers=auth_header())

    json_response = response.get_json()

    user_data = json_response.get('data')
    records_total = json_response.get('records_total')
    records_filtered = json_response.get('records_filtered')

    assert 200 == response.status_code
    assert isinstance(user_data, list)
    assert records_total > 0
    assert records_filtered > 0 and records_filtered <= records_total
    assert user_data[0]['name'].find(user_name) != -1


def test_export_pdf_endpoint(client: FlaskClient, auth_header: any):
    response = client.post('/users/pdf', headers=auth_header())

    try:
        base64.decodebytes(response.data)
    except binascii.Error:
        is_pdf = False
    else:
        is_pdf = True

    assert 200 == response.status_code
    assert is_pdf


def test_export_excel_endpoint(client: FlaskClient, auth_header: any):
    response = client.post('/users/xlsx', headers=auth_header())

    try:
        base64.decodebytes(response.data)
    except binascii.Error:
        is_excel = False
    else:
        is_excel = True

    assert 200 == response.status_code
    assert is_excel
