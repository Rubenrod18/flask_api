import os
from unittest.mock import MagicMock

from marshmallow import ValidationError

from app.services import AuthService
from tests.base.base_api_test import TestBaseApi
from tests.factories.user_factory import UserFactory


class TestValidationErrorHandler(TestBaseApi):
    def test_validation_error_handler(self):
        user = UserFactory(active=True, deleted_at=None)

        mock_auth_service = MagicMock(spec=AuthService)
        sample_error_msg = 'sample error message'
        mock_auth_service.login_user.side_effect = ValidationError(field_name='email', message=sample_error_msg)

        with self.app.container.auth_service.override(mock_auth_service):
            self.app.debug = False
            response = self.client.post(
                f'{self.base_path}/auth/login',
                json={'email': user.email, 'password': os.getenv('TEST_USER_PASSWORD')},
                exp_code=422,
            )
            json_response = response.get_json()

        assert {'message': [sample_error_msg]} == json_response
