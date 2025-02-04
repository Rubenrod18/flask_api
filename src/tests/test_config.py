"""Module for testing Config module."""
from app import create_app


def test_config():
    """Check if TESTING attribute is enabled."""
    assert create_app('config.TestConfig').config.get('TESTING') is True
