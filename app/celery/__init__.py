from celery import Celery, Task
from celery.utils.log import get_task_logger
from flask import Flask

logger = get_task_logger(__name__)


class TaskFailure(Exception):
    pass


class ContextTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo) -> None:
        """
        :param exc: The exception raised by the task.
        :param task_id: Unique id of the failed task.
        :param args: Original arguments for the task that failed.
        :param kwargs: Original keyword arguments for the task that failed.
        :param einfo: ExceptionInfo instance, containing the traceback
        :return: None
        """
        logger.info(f"""
            task id: {task_id}
            args: {args}
            kwargs: {kwargs}
            einfo: {einfo}
            exception: {exc}
        """)


def init_celery(app: Flask) -> Celery:
    celery = Celery(app.import_name)
    celery.conf.update(app.config)

    logger.debug(celery.conf.table(with_defaults=True))

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

    ContextTask.__call__ = __call__

    celery.register_task(ContextTask())
    return celery
