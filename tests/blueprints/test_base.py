from flask.testing import FlaskClient


def test_welcome_api(client: FlaskClient):
    response = client.get('/', json={})

    assert 200 == response.status_code
    assert response.data == b'"Welcome to flask_api!"\n'


def test_get_routes(client: FlaskClient):
    response = client.get('/routes', json={})
    json_response = response.get_json()

    assert 200 == response.status_code
    assert len(json_response.get('routes')) > 0
