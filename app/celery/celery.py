from celery import Celery

celery = Celery('celery')
celery.config_from_object('app.celery.celeryconfig')

if __name__ == '__main__':
    celery.start()
