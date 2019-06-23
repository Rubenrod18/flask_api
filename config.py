import os

from dotenv import load_dotenv

load_dotenv()

class BaseConfig(object):
    """Default configuration options."""
    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIRECTORY = '%s/storage' % ROOT_DIRECTORY
    DEVELOPMENT = False
    DEBUG = False
    LOGIN_DISABLED = False
    DATABASE_NAME = os.environ.get('SQLITE_DB', 'prod.db')
    DATABASE = {
        'name': DATABASE_NAME,
        'engine': 'peewee.SqliteDatabase',
    }

class DevConfig(BaseConfig):
    """Development configuration options."""
    DEVELOPMENT = True
    DEBUG = True
    DATABASE_NAME = os.environ.get('SQLITE_DB', 'dev.db')
    DATABASE = {
        'name': DATABASE_NAME,
        'engine': 'peewee.SqliteDatabase',
    }

class TestConfig(BaseConfig):
    """Testing configuration options."""
    DEVELOPMENT = True
    DATABASE_NAME = os.environ.get('SQLITE_DB', 'test.db')
    TESTING = True
