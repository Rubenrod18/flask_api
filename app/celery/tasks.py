from celery.utils.log import get_task_logger
from flask import render_template
from flask_mail import Message

from app.extensions import mail, celery, ContextTask

logger = get_task_logger(__name__)


@celery.task(name='send_mail_after_create_user', base=ContextTask)
def send_mail_after_create_user(email_data) -> bool:
    logger.info(f'to: {email_data}')

    to = [email_data.get('email')]

    email_args = {
        'subject': 'Welcome to Flask Api!',
        'sender': 'hello@flaskapi.com',
        'recipients': to,
    }
    msg = Message(**email_args)
    msg.html = render_template('mails/new_user.html', **email_data)
    mail.send(msg)
    return True
