import pytest

from app.middleware import ContentTypeValidator, Middleware
from tests.base.base_api_test import TestBaseApi


class TestMiddleware(TestBaseApi):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.validator = ContentTypeValidator(allowed_types={'application/json'})
        self.app.wsgi_app = Middleware(self.app, validator=self.validator)

    def test_api_middleware_invalid_content_type(self):
        response = self.client.post(
            '/api/auth/logout', headers=self.build_headers(extra_headers={'Content-Type': 'text/plain'}), exp_code=400
        )
        json_response = response.get_json()

        assert json_response.get('message'), 'Invalid Content-Type'

    def test_api_middleware_valid_content_type(self):
        self.client.post(
            '/api/auth/logout',
            headers=self.build_headers(extra_headers={'Content-Type': 'application/json'}),
            data={},
            exp_code=200,
        )

    def test_no_api_middleware(self):
        self.client.post('/welcome', exp_code=404)
