from app import create_app


def test_config():
    assert create_app('config.TestConfig').config.get('TESTING') == True
