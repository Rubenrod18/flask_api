from tests.custom_flask_client import CustomFlaskClient


def test_api_middleware(client: CustomFlaskClient, auth_header: any):
    response = client.post('/api/auth/logout', headers=auth_header())
    json_response = response.get_json()

    assert 400 == response.status_code
    assert 'Content type no valid' == json_response.get('message')


def test_no_api_middleware(client: CustomFlaskClient):
    response = client.post('/welcome')
    assert 404 == response.status_code
