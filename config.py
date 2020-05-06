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
        # Sqlite3 recommended settings
        'pragmas': {
            'journal_mode': 'wal',
            'cache_size': -1 * 64000,  # 64MB
            'foreign_keys': 1,
            'ignore_check_constraints': 0,
            'synchronous': 0,
        },
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
    LOG_DIRECTORY = '%s/log' % ROOT_DIRECTORY

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'pyamqp://')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'amqp://')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Etc/Greenwich')
    CELERY_ENABLE_UTC = True
    CELERY_INCLUDE = ['app.celery.tasks']
    CELERY_TASK_TRACK_STARTED = True
    CELERY_RESULT_EXPIRES = 3600
    CELERY_WORKER_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(processName)s - %(message)s'
    CELERY_WORKER_TASK_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(processName)s - %(task_name)s - %(task_id)s - %(message)s'
    CELERY_RESULT_EXTENDED = True


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
