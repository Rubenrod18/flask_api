from tests.base.base_api_test import TestBaseApi


class _BaseAuthIntegrationTest(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/auth'
