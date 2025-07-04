import os

from tests.base.base_api_test import TestBaseApi
from tests.factories.user_factory import UserFactory


class TestGeneralExceptionHandler(TestBaseApi):
    def test_general_exception_handler(self):
        user = UserFactory(active=True, deleted_at=None)

        with self.app.container.auth_service.override(None):
            response = self.client.post(
                f'{self.base_path}/auth/login',
                json={'email': user.email, 'password': os.getenv('TEST_USER_PASSWORD')},
                exp_code=500,
            )
            json_response = response.get_json()

        assert (
            'The server encountered an internal error and was unable to'
            ' complete your request. Either the server is overloaded or'
            ' there is an error in the application.'
        ) == json_response.get('message')
