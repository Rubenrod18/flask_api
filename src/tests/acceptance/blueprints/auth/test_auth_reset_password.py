from unittest import mock

import pytest

from ._base_auth_test import _TestBaseAuthEndpoints


# pylint: disable=attribute-defined-outside-init
class RequestResetPasswordAuthEndpointTest(_TestBaseAuthEndpoints):
    @pytest.fixture(autouse=True)
    def setup_extra(self):
        self.endpoint = f'{self.base_path}/reset_password'

    @mock.patch('app.services.auth.reset_password_email_task.delay', autospec=True)
    def test_request_reset_password(self, mock_reset_password_email_task_delay):
        mock_reset_password_email_task_delay.return_value = True
        payload = {'email': self.admin_user.email}

        self.client.post(self.endpoint, json=payload, exp_code=202)

        mock_reset_password_email_task_delay.assert_called_once()
