import time

from werkzeug.exceptions import BadRequest

from app.helpers.otp_token import OTPTokenManager
from tests.base.base_test import BaseTest


class OTPTokenManagerTest(BaseTest):
    def setUp(self):
        super().setUp()
        self.secret_key = 'test_secret'
        self.salt = 'test_salt'
        self.expiration = 5
        self.manager = OTPTokenManager(self.secret_key, self.salt, self.expiration)

    def test_generate_token(self):
        data = 'test_data'

        token = self.manager.generate_token(data)

        self.assertIsInstance(token, str)

    def test_verify_valid_token(self):
        data = 'test_data'

        token = self.manager.generate_token(data)

        self.assertEqual(self.manager.verify_token(token), data)

    def test_verify_expired_token(self):
        data = 'test_data'

        token = self.manager.generate_token(data)
        time.sleep(self.expiration + 1)
        with self.assertRaises(BadRequest) as context:
            self.manager.verify_token(token)

        self.assertEqual(context.exception.code, 400)
        self.assertEqual(context.exception.description, 'Token expired')

    def test_verify_invalid_token(self):
        invalid_token = 'invalid_token_string'

        with self.assertRaises(BadRequest) as context:
            self.manager.verify_token(invalid_token)

        self.assertEqual(context.exception.code, 400)
        self.assertEqual(context.exception.description, 'Invalid token')
