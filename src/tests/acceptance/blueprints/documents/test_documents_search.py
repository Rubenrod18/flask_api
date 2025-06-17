from datetime import datetime, timedelta, UTC

import pytest

from app.database.factories.document_factory import DocumentFactory

from ._base_documents_test import _TestBaseDocumentEndpoints


class TestSearchDocumentEndpoint(_TestBaseDocumentEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.document = DocumentFactory(
            deleted_at=None,
            created_at=datetime.now(UTC) - timedelta(days=1),
        )
        self.endpoint = f'{self.base_path}/search'

    def test_search_document_endpoint(self):
        payload = {
            'search': [
                {
                    'field_name': 'name',
                    'field_operator': 'eq',
                    'field_value': self.document.name,
                },
            ],
            'order': [
                {
                    'field_name': 'name',
                    'sorting': 'desc',
                },
            ],
        }

        response = self.client.post(self.endpoint, json=payload, headers=self.build_headers(), exp_code=200)
        json_response = response.get_json()

        document_data = json_response.get('data')
        records_total = json_response.get('records_total')
        records_filtered = json_response.get('records_filtered')

        assert isinstance(document_data, list)
        assert records_total > 0
        assert 0 < records_filtered <= records_total
        assert document_data[0].get('name').find(self.document.name) != -1

    def test_check_user_roles_in_search_document_endpoint(self):
        test_cases = [
            (self.admin_user.email, 200),
            (self.team_leader_user.email, 200),
            (self.worker_user.email, 200),
        ]

        for user_email, response_status in test_cases:
            self.client.post(
                self.endpoint, json={}, headers=self.build_headers(user_email=user_email), exp_code=response_status
            )
