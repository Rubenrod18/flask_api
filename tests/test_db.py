from app.extensions import db_wrapper


def test_get_close_db(app):
    with app.app_context():
        db = db_wrapper
        assert db is db_wrapper
        db.database.close()

    is_closed = db.database.is_closed()

    assert is_closed is True
