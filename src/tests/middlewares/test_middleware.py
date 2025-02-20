from tests.base.base_api_test import TestBaseApi


class TestMiddleware(TestBaseApi):
    def setUp(self):
        super(TestMiddleware, self).setUp()

    def test_api_middleware(self):
        response = self.client.post('/api/auth/logout', headers=self.build_headers())
        json_response = response.get_json()

        self.assertEqual(400, response.status_code)
        self.assertEqual('Content type no valid', json_response.get('message'))

    def test_no_api_middleware(self):
        response = self.client.post('/welcome')
        self.assertEqual(404, response.status_code)
