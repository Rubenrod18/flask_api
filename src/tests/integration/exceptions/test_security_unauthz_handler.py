from app.database.factories.user_factory import UserFactory
from tests.base.base_api_test import BaseApiTest


class ExceptionsTest(BaseApiTest):
    def test_custom_unauthorized_handler_exception(self):
        user = UserFactory(active=True, deleted_at=None)

        response = self.client.post(
            '/api/users',
            json={},
            headers=self.build_headers(user_email=user.email),
        )
        json_response = response.get_json()

        self.assertEqual(403, response.status_code, json_response)
        self.assertEqual(
            (
                "You don't have the permission to access the requested resource. "
                'It is either read-protected or not readable by the server.'
            ),
            json_response.get('message'),
        )
