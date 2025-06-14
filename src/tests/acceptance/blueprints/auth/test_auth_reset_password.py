from unittest import mock

from ._base_auth_test import _BaseAuthEndpointsTest


class RequestResetPasswordAuthEndpointTest(_BaseAuthEndpointsTest):
    def setUp(self):
        super().setUp()
        self.endpoint = f'{self.base_path}/reset_password'

    @mock.patch('app.services.auth.reset_password_email_task.delay', autospec=True)
    def test_request_reset_password(self, mock_reset_password_email_task_delay):
        mock_reset_password_email_task_delay.return_value = True
        payload = {'email': self.admin_user.email}

        response = self.client.post(self.endpoint, json=payload, exp_code=202)

        self.assertEqual(202, response.status_code)
        mock_reset_password_email_task_delay.assert_called_once()
