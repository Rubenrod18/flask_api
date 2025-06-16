"""Runs Celery and registers Celery tasks."""

from celery import Celery, Task
from celery.utils.log import get_task_logger
from flask import Flask

logger = get_task_logger(__name__)


class MyCelery(Celery):
    def gen_task_name(self, name, module):
        """New task default automatic naming.

        The default gen_task_name method builds task names based on
        absolute imports, for example:

        project /
                /__init__.py
                /moduleA/
                        /__init.py
                        /tasks.py
                /moduleB/
                        /__init.py
                        /tasks.py

        The default automatic naming is "project.moduleA.tasks.taskA",
        "project.moduleA.tasks.taskB", etc. This new default automatic
        naming forget "tasks" in all task names:

        DEFAULT WAY                         NEW WAY
        project.moduleA.tasks.taskA         project.moduleA.taskA
        project.moduleA.tasks.taskA         project.moduleA.taskB
        project.moduleB.tasks.taskA         project.moduleB.taskA

        This method is only used when the tasks don't have a name
        attribute defined, otherwise, the task name will be respect.

        References
        ----------
        https://docs.celeryproject.org/en/stable/userguide/tasks.html?highlight=gen_task_name#changing-the-automatic-naming-behavior  # noqa # pylint: C0301

        """
        if module.endswith('.tasks'):
            module = module[:-6]
        return super().gen_task_name(name, module)


class ContextTask(Task):
    abstract = True
    queue = 'default'

    def on_failure(self, exc, task_id, args, kwargs, einfo) -> None:
        logger.info(
            f"""
            task id: {task_id}
            args: {args}
            kwargs: {kwargs}
            einfo: {einfo}
            exception: {exc}
        """
        )

    def run(self, *args, **kwargs):
        logger.info('Celery task started')


def make_celery(app: Flask) -> Celery:
    celery = MyCelery(app.import_name)
    celery.conf.update(app.config)
    logger.debug(celery.conf.__dict__)

    def __call__(self, *args, **kwargs):
        """Executes the Celery task within the Flask application context.

        This method overrides the default `__call__` implementation for the custom ContextTask class.
        By wrapping the task execution in `with app.app_context():`, it ensures that Flask's application
        context is available during the execution of the Celery task.

        Notes
        -----
        Without this wrapper, attempting to access Flask-specific features inside a Celery task will raise:
            RuntimeError: Working outside of application context.

        Args
        ----
            *args: Positional arguments passed to the task.
            **kwargs: Keyword arguments passed to the task.

        Returns
        -------
            The result of the task's `run` method.

        """
        with app.app_context():
            return self.run(*args, **kwargs)

    ContextTask.__call__ = __call__
    celery.Task = ContextTask  # pylint: disable=invalid-name

    return celery
