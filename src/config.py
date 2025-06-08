"""Module loads the application's configuration.

The extension and custom configurations are defined here.

"""

import logging
import os
from datetime import timedelta

from dotenv import load_dotenv
from kombu import Exchange, Queue

load_dotenv()


def _str_to_bool(env_value: str, default_env_value: str) -> bool:
    env_value = env_value or default_env_value
    return env_value.lower() == 'true'


class Meta(type):
    """Metaclass for updating Config options."""

    def __new__(mcs, name: str, *args, **kwargs):
        config = super().__new__(mcs, name, *args, **kwargs)
        mcs.new_settings(config)
        return config

    @classmethod
    def new_settings(mcs, config: type) -> None:
        new_settings_names = {
            'SECRET_KEY': 'JWT_SECRET_KEY',
        }

        for current_name, new_name in new_settings_names.items():
            if hasattr(config, current_name):
                setattr(config, new_name, getattr(config, current_name))


class Config(metaclass=Meta):
    """Default configuration options."""

    # Flask
    DEVELOPMENT = False
    DEBUG = False
    TESTING = False
    SERVER_NAME = os.getenv('SERVER_NAME')

    # Flask-Security-Too
    SECRET_KEY = os.getenv('SECRET_KEY')
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT')
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_LENGTH_MIN = 8
    # Enable JWT-based authentication
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'

    #  Flask-JWT-Extended
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Flask SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Flask-Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = _str_to_bool(os.getenv('MAIL_USE_TLS'), 'True')
    MAIL_USE_SSL = _str_to_bool(os.getenv('MAIL_USE_SSL'), 'False')

    # Celery
    broker_url = os.getenv('CELERY_BROKER_URL')
    result_backend = os.getenv('CELERY_RESULT_BACKEND')
    include = [
        'app.celery.tasks',
        'app.celery.excel.tasks',
        'app.celery.word.tasks',
    ]
    task_default_queue = 'default'
    task_queues = (
        Queue('default', Exchange('default'), routing_key='default'),
        Queue('fast', Exchange('tasks'), routing_key='fast'),
    )
    task_track_started = True
    result_expires = 3600
    worker_log_format = '%(asctime)s - %(levelname)s - %(processName)s - %(message)s'
    worker_task_log_format = '%(asctime)s - %(levelname)s - %(processName)s - %(task_name)s - %(task_id)s - %(message)s'
    result_extended = True
    task_default_rate_limit = 3
    task_max_retries = 5
    task_always_eager = False

    # Flask Swagger UI
    SWAGGER_URL = os.getenv('SWAGGER_URL', '/docs')
    SWAGGER_API_URL = os.getenv('SWAGGER_API_URL', f'http://{SERVER_NAME}/static/swagger.yaml')

    # Flask Restx
    RESTX_ERROR_404_HELP = False
    FLASK_RESTFUL_PREFIX = '/api'
    RESTX_MASK_SWAGGER = False

    # Mr Developer
    HOME = os.getenv('HOME')
    LOGGING_LEVEL = logging.INFO

    TEST_USER_EMAIL = os.getenv('TEST_USER_EMAIL')
    TEST_USER_PASSWORD = os.getenv('TEST_USER_PASSWORD')

    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIRECTORY = f'{ROOT_DIRECTORY}/storage'
    MOCKUP_DIRECTORY = f'{ROOT_DIRECTORY}/storage/mockups'
    STATIC_FOLDER = f'{ROOT_DIRECTORY}/static'
    TEMPLATES_FOLDER = f'{ROOT_DIRECTORY}/templates'

    RESET_TOKEN_EXPIRES = 86400  # 1 day = 86400

    ALLOWED_CONTENT_TYPES = {
        'application/json',
        'multipart/form-data',
    }
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/vnd.ms-excel',
    }


class ProdConfig(Config):
    """Production configuration options."""


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

    # Flask SQLAlchemy
    SQLALCHEMY_RECORD_QUERIES = True

    # Mr Developer
    STORAGE_DIRECTORY = f'{Config.STORAGE_DIRECTORY}/tests'
