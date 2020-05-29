from flask.testing import FlaskClient


def test_welcome_api(client: FlaskClient):
    response = client.get('/api', json={})

    assert 200 == response.status_code
    assert response.data == b'"Welcome to flask_api!"\n'
