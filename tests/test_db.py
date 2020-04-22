from app.extensions import db_wrapper


def test_get_close_db():
    db_wrapper.database.close()
    is_closed = db_wrapper.database.is_closed()

    assert is_closed is True
