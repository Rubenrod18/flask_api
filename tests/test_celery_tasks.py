from flask import url_for, Flask
from peewee import fn
from playhouse.shortcuts import model_to_dict

from app.celery.tasks import create_user_email, reset_password_email

from app.models.user import User as UserModel


def test_create_user_email(factory: any):
    user = factory('User').make()
    data = model_to_dict(user)

    task = create_user_email.delay(data)
    result = task.get()

    assert True == result


def test_reset_password_email(app: Flask):
    user = (UserModel.select()
            .where(UserModel.deleted_at.is_null())
            .order_by(fn.Random())
            .limit(1)
            .get())

    token = user.get_reset_token()

    reset_password_url = url_for('auth.resetpasswordresource', token=token, _external=True)
    email_data = {
        'email': user.email,
        'reset_password_url': reset_password_url,
    }

    task = reset_password_email.delay(email_data)
    result = task.get()

    assert True == result
