"""Module for testing basic blueprint."""

from tests.base.base_api_test import TestBaseApi


class TestBasicEndpoints(TestBaseApi):
    def test_welcome_api(self):
        response = self.client.get(f'{self.base_path}/welcome', json={})

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.data, b'"Welcome to flask_api!"\n')
