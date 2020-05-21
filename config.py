import os
from typing import TypeVar

from dotenv import load_dotenv

load_dotenv()

M = TypeVar('M', bound='Meta')


class Meta(type):
    def __new__(cls, name: str, bases: tuple, dict: dict):
        config = super().__new__(cls, name, bases, dict)
        cls._add_celery_new_lowercase_settings(config)
        return config

    @classmethod
    def _add_celery_new_lowercase_settings(cls, config: M) -> None:
        """ https://docs.celeryproject.org/en/latest/userguide/configuration.html#new-lowercase-settings """
        config.broker_url = config.CELERY_BROKER_URL
        config.result_backend = config.CELERY_RESULT_BACKEND
        config.task_serializer = config.CELERY_TASK_SERIALIZER
        config.result_serializer = config.CELERY_RESULT_SERIALIZER
        config.accept_content = config.CELERY_ACCEPT_CONTENT
        config.timezone = config.CELERY_TIMEZONE
        config.enable_utc = config.CELERY_ENABLE_UTC
        config.include = config.CELERY_INCLUDE
        config.task_track_started = config.CELERY_TASK_TRACK_STARTED
        config.result_expires = config.CELERY_RESULT_EXPIRES
        config.worker_log_format = config.CELERY_WORKER_LOG_FORMAT
        config.worker_task_log_format = config.CELERY_WORKER_TASK_LOG_FORMAT
        config.result_extended = config.CELERY_RESULT_EXTENDED
        config.task_default_rate_limit = config.CELERY_TASK_DEFAULT_RATE_LIMIT


class Config(metaclass=Meta):
    """Default configuration options."""
    # Flask
    DEVELOPMENT = False
    DEBUG = False
    TESTING = False
    SERVER_NAME = os.getenv('SERVER_NAME')

    # Flask-Security-Too
    # generated using: secrets.token_urlsafe()
    SECRET_KEY = os.getenv('SECRET_KEY')
    # generated using: secrets.SystemRandom().getrandbits(128)
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
    SECURITY_TOKEN_MAX_AGE = None
    SECURITY_PASSWORD_LENGTH_MIN = 8

    # Peewee
    DATABASE = {
        'name': os.getenv('DATABASE_NAME'),
        'engine': os.getenv('DATABASE_ENGINE', 'peewee.SqliteDatabase'),
        # Sqlite3 recommended settings
        'pragmas': {
            'journal_mode': os.getenv('DATABASE_JOURNAL_MODE', 'wal'),
            'cache_size': os.getenv('DATABASE_CACHE_SIZE', -1 * 64000),  # 64MB
            'foreign_keys': os.getenv('DATABASE_FOREIGN_KEYS', 1),
            'ignore_check_constraints': os.getenv('DATABASE_IGNORE_CHECK_CONSTRAINTS', 0),
            'synchronous': os.getenv('DATABASE_SYNCHRONOUS', 0),
        },
    }

    # Flask-Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'pyamqp://')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'amqp://')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'UTC')
    CELERY_ENABLE_UTC = True
    CELERY_INCLUDE = ['app.celery.tasks']
    CELERY_TASK_TRACK_STARTED = True
    CELERY_RESULT_EXPIRES = 3600
    CELERY_WORKER_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(processName)s - %(message)s'
    CELERY_WORKER_TASK_LOG_FORMAT = '%(asctime)s - %(levelname)s - %(processName)s - %(' \
                                    'task_name)s - %(task_id)s - %(message)s'
    CELERY_RESULT_EXTENDED = True
    CELERY_TASK_DEFAULT_RATE_LIMIT = 3

    # Mr Developer
    HOME = os.getenv('HOME')

    TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL')
    TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD')

    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIRECTORY = '%s/storage' % ROOT_DIRECTORY
    LOG_DIRECTORY = '%s/log' % ROOT_DIRECTORY

    RESET_TOKEN_EXPIRES = 86400  # 1 day = 86400

    ALLOWED_MIME_TYPES = [
        'application/pdf',
        'application/vnd.ms-excel',
    ]


class ProdConfig(Config):
    """Production configuration options."""
    pass


class DevConfig(Config):
    """Development configuration options."""
    DEVELOPMENT = True
    DEBUG = True


class TestConfig(Config):
    """Testing configuration options."""
    DEVELOPMENT = True
    DEBUG = True
    TESTING = True

    DATABASE = {
        'name': 'test.db',
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

    STORAGE_DIRECTORY = '%s/storage/test' % Config.ROOT_DIRECTORY
