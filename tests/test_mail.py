from app.extensions import mail


def test_mail_record_messages(app):
    with mail.record_messages() as outbox:
        mail.send_message(subject='testing',
                          body='test',
                          sender='hello@flaskapi.com',
                          recipients=[app.config.get('TEST_USER_EMAIL')])

        assert len(outbox) == 1
        assert outbox[0].subject == 'testing'
