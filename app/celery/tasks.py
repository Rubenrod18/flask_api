from celery.utils.log import get_task_logger
from flask import render_template
from flask_mail import Message

from app.celery import ContextTask
from app.extensions import mail, celery

logger = get_task_logger(__name__)

@celery.task(name='create_user_email', base=ContextTask)
def create_user_email(email_data) -> bool:
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

@celery.task(name='reset_password_email', base=ContextTask)
def reset_password_email(email_data) -> bool:
    logger.info(f'to: {email_data}')

    to = [email_data.get('email')]

    email_args = {
        'subject': 'Reset password',
        'sender': 'noreply@flaskapi.com',
        'recipients': to,
    }
    msg = Message(**email_args)
    msg.html = render_template('mails/reset_password.html', **email_data)
    mail.send(msg)
    return True
