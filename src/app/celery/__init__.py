"""Runs Celery and registers Celery tasks."""

import logging

from celery import Celery, Task
from flask import Flask


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
        """Handler called when the task fails.

        This method is invoked by Celery if the task raises an exception during execution.
        It logs the failure details using the root logger to ensure proper integration
        with Celery's logging configuration.

        Notes
        -----
        In Celery tasks, it's recommended to use the root 'logging' module directly
        instead of using `get_task_logger(__name__)` or `logging.getLogger(__name__)`.
        This is because Celery configures logging in a way that can interfere with
        logger instances created before Celery has fully initialized,
        potentially causing them to not respect the configured log level or handlers.
        Using the root logger (logging.exception) ensures logs are correctly routed
        according to the Celery logging setup.

        Parameters
        ----------
        exc : Exception
            The exception instance raised by the task.
        task_id : str
            Unique identifier for the task instance.
        args : tuple
            Positional arguments that were passed to the task.
        kwargs : dict
            Keyword arguments that were passed to the task.
        einfo : traceback.TracebackException
            Exception traceback information, useful for detailed debugging.

        Returns
        -------
        None
        """
        logging.exception(
            f""" Celery task "{task_id}" failed:
            task id: {task_id}
            args: {args}
            kwargs: {kwargs}
            einfo: {einfo}
            exception: {exc}
            """
        )

    def run(self, *args, **kwargs):
        """The default entry point for executing the task logic.

        This method is meant to be overridden by subclasses or by the function
        decorated with @celery.task when using ContextTask as the base class.

        Notes
        -----
        When you define a Celery task by decorating a function with
        `@celery.task(base=ContextTask)`, **the decorated function itself replaces
        this `run` method**.

        Therefore, the `run` method defined here in ContextTask is not called
        automatically unless you explicitly subclass ContextTask and override
        the run method.

        In other words, if you write:

            @celery.task(base=ContextTask)
            def my_task(...):
                # task code here

        The `my_task` function becomes the task's `run` method, effectively
        overriding this default `run`.

        This is why you might see `logging.info('Celery task started')` here,
        but it will only be executed if the `run` method itself is directly used
        (for example, in a subclass overriding run).

        This function is an abstract-method and must be overridden.

        Parameters
        ----------
        *args : tuple
            Positional arguments passed to the task.
        **kwargs : dict
            Keyword arguments passed to the task.

        Returns
        -------
        Any
            The return value from the overridden run method or the decorated function.
        """
        logging.info('Celery task started')


def make_celery(app: Flask) -> Celery:
    celery = MyCelery(app.import_name)
    celery.conf.update(app.config)

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
