import os

from app.database.factories.user_factory import AdminUserFactory, TeamLeaderUserFactory, WorkerUserFactory
from tests.base.base_test import TestBase


class TestBaseApi(TestBase):
    def setUp(self):
        super().setUp()
        self.base_path = '/api'
        self.admin_user = AdminUserFactory(
            active=True, deleted_at=None, email=os.getenv('TEST_USER_EMAIL'), password=os.getenv('TEST_USER_PASSWORD')
        )
        self.team_leader_user = TeamLeaderUserFactory(
            active=True, deleted_at=None, password=os.getenv('TEST_USER_PASSWORD')
        )
        self.worker_user = WorkerUserFactory(active=True, deleted_at=None, password=os.getenv('TEST_USER_PASSWORD'))

    def build_headers(self, user_email: str = None, extra_headers: dict = None):
        """Create an auth header from a given user that can be added to http requests."""
        extra_headers = extra_headers or {}

        if user_email is None:
            user_email = self.admin_user.email

        data = {'email': user_email, 'password': self.admin_user.password}

        response = self.client.post('/api/auth/login', json=data)
        json_response = response.get_json()

        assert 200 == response.status_code
        token = json_response['access_token']

        return {self.app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER']: f'Bearer {token}'} | extra_headers
