import os

from flask.testing import FlaskClient
from peewee import fn

from app.extensions import db_wrapper
from app.models.role import Role as RoleModel
from app.models.user import User as UserModel


def test_save_user_endpoint(client: FlaskClient, auth_header: any, factory: any):
    role = RoleModel.get_by_id(1)

    ignore_fields = ['id', 'active', 'created_at', 'updated_at', 'deleted_at', 'created_by']
    data = factory('User').make(exclude=ignore_fields, to_dict=True)
    data['password'] = os.getenv('TEST_USER_PASSWORD')
    data['role_id'] = role.id
    db_wrapper.database.close()

    response = client.post('/api/users', json=data, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 201 == response.status_code
    assert data.get('name') == json_data.get('name')
    assert data.get('last_name') == json_data.get('last_name')
    assert data.get('birth_date') == json_data.get('birth_date')
    assert data.get('genre') == json_data.get('genre')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') == json_data.get('created_at')
    assert json_data.get('deleted_at') is None

    role_data = json_data.get('roles')[0]

    assert role.name == role_data.get('name')
    assert role.label == role_data.get('label')


def test_update_user_endpoint(client: FlaskClient, auth_header: any, factory: any):
    user_id = (UserModel.select(UserModel.id)
               .where(UserModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)

    ignore_fields = ['id', 'active', 'created_at', 'updated_at', 'deleted_at', 'created_by']
    data = factory('User').make(to_dict=True, exclude=ignore_fields)

    data['password'] = os.getenv('TEST_USER_PASSWORD')
    role = (RoleModel.select()
            .where(RoleModel.deleted_at.is_null())
            .order_by(fn.Random())
            .limit(1)
            .get())
    data['role_id'] = role.id
    db_wrapper.database.close()

    response = client.put('/api/users/%s' % user_id, json=data, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert user_id == json_data.get('id')
    assert data.get('name') == json_data.get('name')
    assert data.get('last_name') == json_data.get('last_name')
    assert data.get('birth_date') == json_data.get('birth_date')
    assert data.get('genre') == json_data.get('genre')
    assert json_data.get('created_at')
    assert json_data.get('updated_at') >= json_data.get('created_at')
    assert json_data.get('deleted_at') is None

    role_data = json_data.get('roles')[0]

    assert role.name == role_data.get('name')
    assert role.label == role_data.get('label')


def test_get_user_endpoint(client: FlaskClient, auth_header: any):
    user_id = (UserModel.select(UserModel.id)
               .where(UserModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)

    user = UserModel.get(UserModel.id == user_id)
    role = user.roles[0]
    db_wrapper.database.close()

    response = client.get('/api/users/%s' % user_id, json={}, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    assert 200 == response.status_code
    assert user_id == json_data.get('id')
    assert user.name == json_data.get('name')
    assert user.last_name == json_data.get('last_name')
    assert user.birth_date.strftime('%Y-%m-%d') == json_data.get('birth_date')
    assert user.created_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('created_at')
    assert user.updated_at.strftime('%Y-%m-%d %H:%M:%S') == json_data.get('updated_at')
    assert user.deleted_at == json_data.get('deleted_at')

    role_data = json_data.get('roles')[0]

    assert role.name == role_data.get('name')
    assert role.label == role_data.get('label')


def test_delete_user_endpoint(client: FlaskClient, auth_header: any):
    user_id = (UserModel.select(UserModel.id)
               .where(UserModel.deleted_at.is_null())
               .order_by(fn.Random())
               .limit(1)
               .get()
               .id)
    db_wrapper.database.close()

    response = client.delete('/api/users/%s' % user_id, json={}, headers=auth_header())
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
                'field_operator': 'eq',
                'field_value': user_name,
            },
        ],
        'order': [
            ['name', 'desc'],
        ],
    }

    response = client.post('/api/users/search', json=json_body, headers=auth_header())
    json_response = response.get_json()

    user_data = json_response.get('data')
    records_total = json_response.get('records_total')
    records_filtered = json_response.get('records_filtered')

    assert 200 == response.status_code
    assert isinstance(user_data, list)
    assert records_total > 0
    assert 0 < records_filtered <= records_total
    assert user_data[0]['name'].find(user_name) != -1


def test_export_word_endpoint(client: FlaskClient, auth_header: any):
    def _request(uri: str, headers: str, json: dict) -> None:
        response = client.post(uri, json=json, headers=headers)
        json_response = response.get_json()

        assert 202 == response.status_code
        assert json_response.get('task')
        assert json_response.get('url')

    json = {
        'search': [],
        'order': [
            ['name', 'desc'],
        ],
    }

    _request('/api/users/word', auth_header(), json)
    _request('/api/users/word?to_pdf=1', auth_header(), json)
    _request('/api/users/word?to_pdf=0', auth_header(), json)


def test_export_excel_endpoint(client: FlaskClient, auth_header: any):
    data = {}

    response = client.post('/api/users/xlsx', json=data, headers=auth_header())
    json_response = response.get_json()

    assert 202 == response.status_code
    assert json_response.get('task')
    assert json_response.get('url')
