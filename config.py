"""Module loads the application's configuration.

The extension and custom configurations are defined here.

"""
import os

import celery
from dotenv import load_dotenv

load_dotenv()


class Meta(type):
    """Metaclass for updating Config options."""
    def __new__(cls, name: str, bases: tuple, dict: dict):
        config = super().__new__(cls, name, bases, dict)
        cls._rename_celery_settings(config)
        return config

    @classmethod
    def _rename_celery_settings(cls, config: type) -> None:
        """Rename old Celery setting names with new ones.

        References
        ----------
        https://docs.celeryproject.org/en/latest/userguide/configuration.html#new-lowercase-settings

        """
        new_settings_names = {
            'CELERY_BROKER_URL': 'broker_url',
            'CELERY_RESULT_BACKEND': 'result_backend',
            'CELERY_TASK_SERIALIZER': 'task_serializer',
            'CELERY_RESULT_SERIALIZER': 'result_serializer',
            'CELERY_ACCEPT_CONTENT': 'accept_content',
            'CELERY_TIMEZONE': 'timezone',
            'CELERY_ENABLE_UTC': 'enable_utc',
            'CELERY_INCLUDE': 'include',
            'CELERY_TASK_TRACK_STARTED': 'task_track_started',
            'CELERY_RESULT_EXPIRES': 'result_expires',
            'CELERY_WORKER_LOG_FORMAT': 'worker_log_format',
            'CELERY_WORKER_TASK_LOG_FORMAT': 'worker_task_log_format',
            'CELERY_RESULT_EXTENDED': 'result_extended',
            'CELERY_TASK_DEFAULT_RATE_LIMIT': 'task_default_rate_limit',
            'CELERY_TASK_ALWAYS_EAGER': 'task_always_eager',
        }

        for current_name, new_name in new_settings_names.items():
            if hasattr(config, current_name):
                setattr(config, new_name, getattr(config, current_name))
                delattr(config, current_name)


class Config(metaclass=Meta):
    """Default configuration options."""
    # Flask
    DEVELOPMENT = False
    DEBUG = False
    TESTING = False
    SERVER_NAME = os.getenv('SERVER_NAME')
    LOGIN_DISABLED = False

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
        # http://docs.peewee-orm.com/en/latest/peewee/database.html?highlight=%22recommended%20settings%22#recommended-settings
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
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', False)

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
    CELERY_WORKER_LOG_FORMAT = ('%(asctime)s - %(levelname)s - '
                                '%(processName)s - %(message)s')
    CELERY_WORKER_TASK_LOG_FORMAT = ('%(asctime)s - %(levelname)s - '
                                     '%(processName)s - %(task_name)s - '
                                     '%(task_id)s - %(message)s')
    CELERY_RESULT_EXTENDED = True
    CELERY_TASK_DEFAULT_RATE_LIMIT = 3
    CELERY_TASK_ALWAYS_EAGER = False

    # Flask Swagger UI
    SWAGGER_URL = os.getenv('SWAGGER_URL', '/docs')
    SWAGGER_API_URL = os.getenv(
        'SWAGGER_API_URL', f'http://{SERVER_NAME}/static/swagger.yaml'
    )

    # Flask Restful
    ERROR_404_HELP = False
    FLASK_RESTFUL_PREFIX = '/api'
    RESTX_MASK_SWAGGER = False

    # Mr Developer
    HOME = os.getenv('HOME')

    TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL')
    TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD')

    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIRECTORY = '%s/storage' % ROOT_DIRECTORY
    MOCKUP_DIRECTORY = '%s/storage/mockups' % ROOT_DIRECTORY
    LOG_DIRECTORY = '%s/log' % ROOT_DIRECTORY

    RESET_TOKEN_EXPIRES = 86400  # 1 day = 86400

    ALLOWED_CONTENT_TYPES = {
        'application/json',
        'multipart/form-data',
        'application/octet-stream',
    }
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.ms-excel',
    }


class ProdConfig(Config):
    """Production configuration options."""
    pass


class DevConfig(Config):
    """Development configuration options."""
    # Flask
    DEVELOPMENT = True
    DEBUG = True


class TestConfig(Config):
    """Testing configuration options."""
    # Flask
    DEVELOPMENT = True
    DEBUG = True
    TESTING = True

    # Peewee
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

    # Mr Developer
    STORAGE_DIRECTORY = f'{Config.STORAGE_DIRECTORY}/tests'
