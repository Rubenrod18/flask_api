from celery import Celery

app = Celery('celery')
app.config_from_object('app.celery.celeryconfig')

app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()