from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.exceptions import BadRequest


class OTPTokenManager:
    def __init__(self, secret_key: str, salt: str, expiration: int):
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.salt = salt
        self.expiration = expiration

    def generate_token(self, data: str) -> str:
        return self.serializer.dumps(data, salt=self.salt)

    def verify_token(self, token: str) -> str | None:
        try:
            return self.serializer.loads(token, salt=self.salt, max_age=self.expiration)
        except SignatureExpired as exc:
            raise BadRequest('Token expired') from exc
        except BadSignature as exc:
            raise BadRequest('Invalid token') from exc
