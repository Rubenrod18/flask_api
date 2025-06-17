"""Module for testing mail."""

from flask import current_app

from app.extensions import mail


# pylint: disable=attribute-defined-outside-init, unused-argument
class TestMail:
    def test_mail_record_messages(self, app, faker):
        """Check if an email is sent."""
        with mail.record_messages() as outbox:
            subject = faker.sentence()

            mail.send_message(
                subject=subject,
                body=faker.text(),
                sender=faker.email(),
                recipients=[current_app.config.get('TEST_USER_EMAIL')],
            )

            assert len(outbox) == 1
            assert outbox[0].subject == subject
