from tests.base.base_api_test import TestBaseApi


class _BaseDocumentsIntegrationTest(TestBaseApi):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/documents'
