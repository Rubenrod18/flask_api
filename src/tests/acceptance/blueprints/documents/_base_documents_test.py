from tests.base.base_api_test import BaseApiTest


class _BaseDocumentEndpointsTest(BaseApiTest):
    def setUp(self):
        super().setUp()
        self.base_path = f'{self.base_path}/documents'
