from tests.base.base_api_test import BaseApiTest


class _BaseRoleEndpointsTest(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/roles'
