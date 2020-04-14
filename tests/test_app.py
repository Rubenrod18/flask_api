import base64
import binascii

from peewee import fn
from playhouse.shortcuts import model_to_dict

from app import create_app
from app.extensions import db_wrapper
from app.models.user import User


def test_config():
    assert create_app('config.TestConfig').config.get('TESTING')


def test_welcome_api(client):
    response = client.get('/')

    assert 200 == response.status_code
    assert response.data == b'"Welcome to flask_api!"\n'


def test_save_user_endpoint(client):
    user = User.fake()

    data = model_to_dict(user)
    del data['id']
    del data['created_at']
    del data['updated_at']
    del data['deleted_at']

    response = client.post('/users', json=data)

    json_response = response.get_json()
    json_user_data = json_response.get('data')

    assert 201 == response.status_code
    assert data.get('name') == json_user_data.get('name')
    assert data.get('last_name') == json_user_data.get('last_name')
    assert data.get('age') == json_user_data.get('age')
    assert data.get('birth_date') == json_user_data.get('birth_date')
    assert json_user_data.get('created_at')
    assert json_user_data.get('updated_at') == json_user_data.get('created_at')
    assert json_user_data.get('deleted_at') is None


def test_update_user_endpoint(client):
    user_id = (User.select(User.id)
                   .order_by(fn.Random())
                   .limit(1)
                   .get()
                   .id)
    db_wrapper.database.close()

    user = User.fake()

    data = model_to_dict(user)
    del data['id']
    del data['created_at']
    del data['updated_at']
    del data['deleted_at']

    response = client.put('/users/%s' % user_id, json=data)

    json_response = response.get_json()
    json_user_data = json_response.get('data')

    assert 200 == response.status_code
    assert user_id == json_user_data.get('id')
    assert data.get('name') == json_user_data.get('name')
    assert data.get('last_name') == json_user_data.get('last_name')
    assert data.get('age') == json_user_data.get('age')
    assert data.get('birth_date') == json_user_data.get('birth_date')
    assert json_user_data.get('created_at')
    assert json_user_data.get('updated_at') > json_user_data.get('created_at')
    assert json_user_data.get('deleted_at') is None


def test_delete_user_endpoint(client):
    user_id = (User.select(User.id)
                   .order_by(fn.Random())
                   .limit(1)
                   .get()
                   .id)
    db_wrapper.database.close()

    response = client.delete('/users/%s' % user_id)

    json_response = response.get_json()
    json_user_data = json_response.get('data')

    assert 200 == response.status_code
    assert user_id == json_user_data.get('id')
    assert json_user_data.get('deleted_at') is not None
    assert json_user_data.get('deleted_at') >= json_user_data.get('updated_at')


def test_search_users_endpoint(client):
    json_body = {
        'search': [
            {
                'field_name': 'id',
                'field_value': ''
            }
        ],
        'order': 'desc',
        'sort': 'id'
    }

    response = client.post('/users/search', json=json_body)

    json_response = response.get_json()

    user_data = json_response.get('data')
    records_total = json_response.get('records_total')
    records_filtered = json_response.get('records_filtered')

    assert 200 == response.status_code
    assert isinstance(user_data, list)
    assert records_total > 0
    assert records_filtered > 0 and records_filtered <= records_total


def test_export_pdf_endpoint(client):
    response = client.post('/users/pdf')

    try:
        base64.decodebytes(response.data)
    except binascii.Error:
        is_pdf = False
    else:
        is_pdf = True

    assert 200 == response.status_code
    assert is_pdf


def test_export_excel_endpoint(client):
    response = client.post('/users/xlsx')

    try:
        base64.decodebytes(response.data)
    except binascii.Error:
        is_excel = False
    else:
        is_excel = True

    assert 200 == response.status_code
    assert is_excel
