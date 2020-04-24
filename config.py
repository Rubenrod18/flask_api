import os


class BaseConfig(object):
    """Default configuration options."""
    ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
    STORAGE_DIRECTORY = '%s/storage' % ROOT_DIRECTORY
    DEVELOPMENT = False
    DEBUG = False
    LOGIN_DISABLED = False

    DATABASE_NAME = os.environ.get('SQLITE_DB', 'prod')
    DATABASE_FILEPATH = '%s/%s.db' % (ROOT_DIRECTORY, DATABASE_NAME)
    DATABASE = {
        'name': DATABASE_FILEPATH,
        'engine': 'peewee.SqliteDatabase',
    }


class DevConfig(BaseConfig):
    """Development configuration options."""
    DEVELOPMENT = True
    DEBUG = True

    DATABASE_NAME = os.environ.get('SQLITE_DB', 'dev')
    DATABASE_FILEPATH = '%s/%s.db' % (BaseConfig.ROOT_DIRECTORY, DATABASE_NAME)
    DATABASE = {
        'name': DATABASE_FILEPATH,
        'engine': 'peewee.SqliteDatabase',
    }


class TestConfig(BaseConfig):
    """Testing configuration options."""
    DEVELOPMENT = True
    TESTING = True

    DATABASE_NAME = os.environ.get('SQLITE_DB', 'test')
    DATABASE_FILEPATH = '%s/%s.db' % (BaseConfig.ROOT_DIRECTORY, DATABASE_NAME)
    DATABASE = {
        'name': DATABASE_FILEPATH,
        'engine': 'peewee.SqliteDatabase',
    }
