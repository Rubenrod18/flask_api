import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig(object):
    """Default configuration options."""
    DEVELOPMENT = False
    DEBUG = False

    DATABASE = {
        'name': os.getenv('DATABASE_NAME'),
        'engine': 'peewee.SqliteDatabase',
    }
    TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL')
    TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD')

    # SECRET_KEY generated using: secrets.token_urlsafe()
    SECRET_KEY = os.getenv('SECRET_KEY')
    # PASSWORD_SALT secrets.SystemRandom().getrandbits(128)
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
    SECURITY_TOKEN_MAX_AGE = None
    SECURITY_PASSWORD_LENGTH_MIN = 5

    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIRECTORY = '%s/storage' % ROOT_DIRECTORY


class DevConfig(BaseConfig):
    """Development configuration options."""
    DEVELOPMENT = True
    DEBUG = True


class TestConfig(BaseConfig):
    """Testing configuration options."""
    DEVELOPMENT = True
    TESTING = True

    DATABASE = {
        'name': 'test.db',
        'engine': 'peewee.SqliteDatabase',
    }
