"""Module for testing basic blueprint."""
from tests.base.base_api_test import TestBaseApi


class TestBasicEndpoints(TestBaseApi):
    def setUp(self):
        super(TestBasicEndpoints, self).setUp()

    def test_welcome_api(self):
        response = self.client.get(f'{self.base_path}/welcome', json={})

        assert 200 == response.status_code
        assert response.data == b'"Welcome to flask_api!"\n'
