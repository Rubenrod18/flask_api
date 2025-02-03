"""Module for testing database."""
from app.extensions import db_wrapper


def test_get_close_db():
    """Check if a database connection is closed."""

    is_closed = db_wrapper.database.is_closed()

    assert is_closed is True
