import os


class BaseConfig(object):
    """Default configuration options."""
    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIRECTORY = '%s/storage' % ROOT_DIRECTORY
    DEVELOPMENT = False
    DEBUG = False
    LOGIN_DISABLED = False

    DATABASE_NAME = os.environ.get('SQLITE_DB', 'prod')
    DATABASE_FILENAME = '%s.db' % DATABASE_NAME
    DATABASE = {
        'name': DATABASE_FILENAME,
        'engine': 'peewee.SqliteDatabase',
    }


class DevConfig(BaseConfig):
    """Development configuration options."""
    DEVELOPMENT = True
    DEBUG = True

    DATABASE_NAME = os.environ.get('SQLITE_DB', 'dev')
    DATABASE_FILENAME = '%s.db' % DATABASE_NAME
    DATABASE = {
        'name': DATABASE_FILENAME,
        'engine': 'peewee.SqliteDatabase',
    }


class TestConfig(BaseConfig):
    """Testing configuration options."""
    DEVELOPMENT = True
    TESTING = True

    DATABASE_NAME = os.environ.get('SQLITE_DB', 'test')
    DATABASE_FILENAME = '%s.db' % DATABASE_NAME
    DATABASE = {
        'name': DATABASE_FILENAME,
        'engine': 'peewee.SqliteDatabase',
    }
