"""Module loads the application's configuration.

The extension and custom configurations are defined here.

"""
import logging
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
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

    # Flask SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Flask-Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', True)
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', False)

    # Celery
    broker_url = os.getenv('CELERY_BROKER_URL', 'pyamqp://')
    result_backend = os.getenv('CELERY_RESULT_BACKEND', 'rpc://')
    include = ['app.celery.tasks']
    task_track_started = True
    result_expires = 3600
    worker_log_format = '%(asctime)s - %(levelname)s - %(processName)s - %(message)s'
    worker_task_log_format = '%(asctime)s - %(levelname)s - %(processName)s - %(task_name)s - %(task_id)s - %(message)s'
    result_extended = True
    task_default_rate_limit = 3
    task_always_eager = False

    # Flask Swagger UI
    SWAGGER_URL = os.getenv('SWAGGER_URL', '/docs')
    SWAGGER_API_URL = os.getenv(
        'SWAGGER_API_URL', f'http://{SERVER_NAME}/static/swagger.yaml'
    )

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

    # Flask SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_RECORD_QUERIES = True

    # Mr Developer
    STORAGE_DIRECTORY = f'{Config.STORAGE_DIRECTORY}/tests'
