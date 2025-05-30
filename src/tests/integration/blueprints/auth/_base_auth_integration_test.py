from tests.base.base_api_test import BaseApiTest


class _BaseAuthEndpointsTest(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/auth'
