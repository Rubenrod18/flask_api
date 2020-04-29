import os

from dotenv import load_dotenv

load_dotenv()


class BaseConfig(object):
    """Default configuration options."""
    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIRECTORY = '%s/storage' % ROOT_DIRECTORY
    DEVELOPMENT = False
    DEBUG = False

    DATABASE = {
        'name': os.getenv('DATABASE_NAME'),
        'engine': 'peewee.SqliteDatabase',
    }

    # SECRET_KEY generated using: secrets.token_urlsafe()
    SECRET_KEY = os.getenv('SECRET_KEY')
    # PASSWORD_SALT secrets.SystemRandom().getrandbits(128)
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')

    TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL')
    TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD')


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
