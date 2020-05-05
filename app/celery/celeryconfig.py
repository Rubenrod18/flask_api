broker_url = 'pyamqp://'
result_backend = 'amqp://'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Europe/Madrid'
enable_utc = True
include=['app.celery.tasks']