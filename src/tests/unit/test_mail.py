"""Module for testing mail."""

from app.extensions import mail
from tests.base.base_test import BaseTest


class MailTest(BaseTest):
    def test_mail_record_messages(self):
        """Check if an email is sent."""
        with mail.record_messages() as outbox:
            subject = self.faker.sentence()

            mail.send_message(
                subject=subject,
                body=self.faker.text(),
                sender=self.faker.email(),
                recipients=[self.app.config.get('TEST_USER_EMAIL')],
            )

            self.assertEqual(len(outbox), 1)
            self.assertEqual(outbox[0].subject, subject)
