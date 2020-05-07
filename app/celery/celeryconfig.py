from config import BaseConfig

config = BaseConfig()

# General settings
accept_content = config.CELERY_ACCEPT_CONTENT

# Broker settings
broker_url = config.CELERY_BROKER_URL

# Task result backend settings
result_backend = config.CELERY_RESULT_BACKEND
result_serializer = config.CELERY_RESULT_SERIALIZER
result_expires = config.CELERY_RESULT_EXPIRES
result_extended = config.CELERY_RESULT_EXTENDED

# Task settings
task_serializer = config.CELERY_TASK_SERIALIZER

# Time and date settings
timezone = config.CELERY_TIMEZONE
enable_utc = config.CELERY_ENABLE_UTC

# Worker
include = config.CELERY_INCLUDE

# Task execution settings
task_track_started = config.CELERY_TASK_TRACK_STARTED

# Logging
worker_log_format = config.CELERY_WORKER_LOG_FORMAT
worker_task_log_format = config.CELERY_WORKER_TASK_LOG_FORMAT