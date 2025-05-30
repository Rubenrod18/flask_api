from tests.base.base_api_test import BaseApiTest


class _BaseUserEndpointsTest(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/users'
