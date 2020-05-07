from app import init_celery, create_app

flask_app = create_app('config.DevConfig')
celery = init_celery(flask_app)

if __name__ == '__main__':
    celery.run()