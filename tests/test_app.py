from peewee import fn
from playhouse.shortcuts import model_to_dict

from app import create_app
from app.models.user import User


def test_config():
    assert create_app('config.TestConfig').config.get('TESTING')


def test_welcome_api(client):
    response = client.get('/')

    assert 200 == response.status_code
    assert response.data == b'"Welcome to flask_api!"\n'


def test_save_user(client):
    user = User.fake()

    data = model_to_dict(user)

    response = client.post('/users', json=data)

    assert 201 == response.status_code
    assert response.data == b'{"data": 1}\n'


def test_update_user(client):
    user_id = (User.select(User.id)
                   .order_by(fn.Random())
                   .limit(1)
                   .get()
                   .id)
    user = User.fake()

    data = model_to_dict(user)

    response = client.put('/users/%s' % user_id, json=data)

    json_data = response.get_json()
    json_user_data = json_data.get('data')

    assert 200 == response.status_code
    assert user_id == json_user_data.get('id')
    assert data.get('name') == json_user_data.get('name')
    assert data.get('last_name') == json_user_data.get('last_name')
    assert data.get('age') == json_user_data.get('age')
    assert data.get('birth_date') == json_user_data.get('birth_date')
    assert json_user_data.get('created_at')
    assert json_user_data.get('created_at') < json_user_data.get('updated_at')
    assert json_user_data.get('deleted_at') is None


def test_delete_user(client):
    user_id = (User.select(User.id)
                   .order_by(fn.Random())
                   .limit(1)
                   .get()
                   .id)

    response = client.delete('/users/%s' % user_id)

    json_data = response.get_json()
    json_user_data = json_data.get('data')

    assert 200 == response.status_code
    assert user_id == json_user_data.get('id')
    assert json_user_data.get('deleted_at') is not None
    assert json_user_data.get('deleted_at') >= json_user_data.get('updated_at')
