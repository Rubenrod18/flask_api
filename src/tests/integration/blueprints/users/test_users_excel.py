from ._base_integration_test import _BaseUserEndpointsTest


class WordUserEndpointTest(_BaseUserEndpointsTest):
    def setUp(self):
        super().setUp()
        self.endpoint = f'{self.base_path}/word'

    def test_export_word_endpoint(self):
        auth_headers = self.build_headers()
        test_cases = [
            (f'{self.base_path}/word', auth_headers, {}),
            (f'{self.base_path}/word?to_pdf=1', auth_headers, {}),
            (f'{self.base_path}/word?to_pdf=0', auth_headers, {}),
        ]

        for uri, auth_headers, payload in test_cases:
            with self.subTest(uri=uri):
                response = self.client.post(uri, json=payload, headers=auth_headers)
                json_response = response.get_json()

                self.assertEqual(202, response.status_code)
                self.assertTrue(json_response.get('task'))
                self.assertTrue(json_response.get('url'))

    def test_check_user_roles_in_export_word_endpoint(self):
        test_cases = [
            (self.admin_user.email, 202),
            (self.team_leader_user.email, 202),
            (self.worker_user.email, 202),
        ]

        for user_email, response_status in test_cases:
            with self.subTest(user_email=user_email):
                response = self.client.post(
                    f'{self.base_path}/word', json={}, headers=self.build_headers(user_email=user_email)
                )
                json_response = response.get_json()

                self.assertEqual(response_status, response.status_code, json_response)
