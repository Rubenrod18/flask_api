from celery import states
from celery.result import AsyncResult
from flask_login import current_user

from app.celery.excel.tasks import export_user_data_in_excel_task
from app.celery.tasks import create_user_email_task, create_word_and_excel_documents_task, reset_password_email_task
from app.celery.word.tasks import export_user_data_in_word_task


class TaskService:
    @staticmethod
    def check_task_status(task_id: str) -> dict:
        task_data = AsyncResult(task_id)
        response = {'state': task_data.state}

        if task_data.state == states.PENDING:
            response.update({'current': 0, 'total': 1})
        elif task_data.state in [states.STARTED, states.SUCCESS]:
            response.update(task_data.info)
        else:
            response.update({'current': 1, 'total': 1})

        return response

    @staticmethod
    def send_create_user_email(**kwargs) -> None:
        create_user_email_task.delay(kwargs)

    @staticmethod
    def reset_password_email(**kwargs) -> None:
        reset_password_email_task.delay(kwargs)

    @staticmethod
    def export_user_data_in_excel(data: dict) -> AsyncResult:
        return export_user_data_in_excel_task.apply_async((current_user.id, data), countdown=5)

    @staticmethod
    def export_user_data_in_word(data: dict, request_args: dict) -> AsyncResult:
        to_pdf = request_args.get('to_pdf', 0)
        return export_user_data_in_word_task.apply_async(args=[current_user.id, data, to_pdf])

    @staticmethod
    def export_user_data_in_excel_and_word(data: dict, request_args) -> AsyncResult:
        to_pdf = request_args.get('to_pdf', 0)

        return create_word_and_excel_documents_task.apply_async(args=[current_user.id, data, to_pdf])
