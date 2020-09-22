from celery import Celery, Task
from celery.utils.log import get_task_logger
from flask import Flask

logger = get_task_logger(__name__)


class TaskFailure(Exception):
    pass


class MyCelery(Celery):
    def gen_task_name(self, name, module):
        """New task default automatic naming.


        The default gen_task_name method builds task names based on absolute
        imports, for example:

        project /
                /__init__.py
                /moduleA/
                        /__init.py
                        /tasks.py
                /moduleB/
                        /__init.py
                        /tasks.py

        The default automatic naming is "project.moduleA.tasks.taskA",
        "project.moduleA.tasks.taskB", etc. This new default automatic naming
        forget "tasks" in all task names:

        DEFAULT WAY                         NEW WAY
        project.moduleA.tasks.taskA         project.moduleA.taskA
        project.moduleA.tasks.taskA         project.moduleA.taskB
        project.moduleB.tasks.taskA         project.moduleB.taskA

        This method is only used when the tasks don't have a name attribute
        defined, otherwise, the task name will be respect.

        https://docs.celeryproject.org/en/stable/userguide/tasks.html?highlight=gen_task_name#changing-the-automatic-naming-behavior
        """
        if module.endswith('.tasks'):
            module = module[:-6]
        return super(MyCelery, self).gen_task_name(name, module)


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
    celery = MyCelery(app.import_name)
    celery.conf.update(app.config)

    logger.debug(celery.conf.table(with_defaults=True))

    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

    ContextTask.__call__ = __call__

    celery.register_task(ContextTask())
    return celery
