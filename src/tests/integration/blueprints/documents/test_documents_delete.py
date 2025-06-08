from datetime import datetime, timedelta, UTC

from app.database.factories.document_factory import DocumentFactory
from tests.integration.blueprints.documents._base_integration_test import _BaseDocumentEndpointsTest


class DeleteDocumentEndpointTest(_BaseDocumentEndpointsTest):
    def setUp(self):
        super().setUp()
        self.document = DocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        self.endpoint = f'{self.base_path}/{self.document.id}'

    def test_delete_document_endpoint(self):
        response = self.client.delete(self.endpoint, json={}, headers=self.build_headers())
        json_response = response.get_json()
        json_data = json_response.get('data')

        self.assertEqual(self.document.id, json_data.get('id'))
        self.assertIsNotNone(json_data.get('deleted_at'))
        self.assertGreaterEqual(json_data.get('deleted_at'), json_data.get('updated_at'))

    def test_check_user_roles_in_delete_document_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 404),
            (self.worker_user.email, 404),
        ]

        for user_email, response_status in test_cases:
            self.client.delete(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
