"""

TODO: Temporal solution.

If you would like to run all tests then you must change next env vars values

- CELERY_BROKER_URL equal to TEST_CELERY_BROKER_URL value
- CELERY_RESULT_BACKEND equal to TEST_CELERY_RESULT_BACKEND value
- FLASK_APP equal to `manage.py`
- FLASK_CONFIG equal to `config.TestConfig`

And start up the Celery and Flower service in your local environment instead of the Docker.
Before to run next commands you need to have activate your virtual environment with the requirements-dev packages
installed.

1. Stop the Docker images: celery and flower
    >>> docker stop flask_api_celery flask_api_flower

Celery:
    >>> flask celery

Flower:
    >>> celery -A app.celery flower --address=127.0.0.1 --port=5555

"""

import logging

logger = logging.getLogger(__name__)
