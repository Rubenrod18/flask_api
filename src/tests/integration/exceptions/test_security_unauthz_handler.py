from tests.base.base_api_test import TestBaseApi
from tests.factories.user_factory import UserFactory


class TestExceptions(TestBaseApi):
    def test_custom_unauthorized_handler_exception(self):
        user = UserFactory(active=True, deleted_at=None)

        response = self.client.post(
            '/api/users', json={}, headers=self.build_headers(user_email=user.email), exp_code=403
        )
        json_response = response.get_json()

        assert (
            "You don't have the permission to access the requested resource. "
            'It is either read-protected or not readable by the server.'
        ) == json_response.get('message')
