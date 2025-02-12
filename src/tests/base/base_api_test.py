import os

from app.extensions import db
from app.models import User
from database.factories.user_factory import AdminUserFactory
from tests.base.base_test import TestBase


class TestBaseApi(TestBase):
    def setUp(self):
        super(TestBaseApi, self).setUp()
        self.base_path = '/api'
        self.admin_user = self.get_active_admin_user()

    @staticmethod
    def get_active_admin_user():
        user = db.session.query(User).filter_by(email=os.getenv('TEST_USER_EMAIL')).first()

        if user is None:
            return AdminUserFactory(active=True, deleted_at=None, email=os.getenv('TEST_USER_EMAIL'), password=os.getenv('TEST_USER_PASSWORD'))

        return user

    def build_headers(self, user_email: str = None, extra_headers: dict = None):
        """Create an auth header from a given user that can be added to http requests."""
        extra_headers = extra_headers or {}

        if user_email is None:
            user_email = self.admin_user.email

        data = {'email': user_email, 'password': self.admin_user.password}

        response = self.client.post('/api/auth/login', json=data)
        json_response = response.get_json()

        assert 200 == response.status_code
        token = json_response.get('token')

        return {self.app.config['SECURITY_TOKEN_AUTHENTICATION_HEADER']: token} | extra_headers
