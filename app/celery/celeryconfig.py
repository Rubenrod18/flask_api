from flask import current_app

from manage import app

with app.app_context():
    config = current_app.config

# General settings
accept_content = config.get('CELERY_ACCEPT_CONTENT')

# Broker settings
broker_url = config.get('CELERY_BROKER_URL')

# Task result backend settings
result_backend = config.get('CELERY_RESULT_BACKEND')
result_serializer = config.get('CELERY_RESULT_SERIALIZER')
result_expires = config.get('CELERY_RESULT_EXPIRES')
result_extended = config.get('CELERY_RESULT_EXTENDED')

# Task settings
task_serializer = config.get('CELERY_TASK_SERIALIZER')

# Time and date settings
timezone = config.get('CELERY_TIMEZONE')
enable_utc = config.get('ENABLE_UTC')

# Worker
include = config.get('CELERY_INCLUDE')

# Task execution settings
task_track_started = config.get('CELERY_TASK_TRACK_STARTED')

# Logging
worker_log_format = config.get('CELERY_WORKER_LOG_FORMAT')
worker_task_log_format = config.get('WORKER_TASK_LOG_FORMAT')