from flask import current_app

from app.extensions import db_wrapper
from app.managers import BaseManager
from tests.custom_flask_client import CustomFlaskClient


def test_check_task_status(client: CustomFlaskClient, auth_header: any):
    def create_task_table():
        sql_file = ('%s/create_task_table.sql'
                    % current_app.config.get('STORAGE_DIRECTORY'))
        with open(sql_file, 'r') as fp:
            sql = fp.read()

        base_manager = BaseManager()
        base_manager.raw(sql)
        db_wrapper.database.close()

    def insert_task_record():
        sql_file = ('%s/create_task_record.sql'
                    % current_app.config.get('STORAGE_DIRECTORY'))
        with open(sql_file, 'r') as fp:
            sql = fp.read()

        base_manager = BaseManager()
        base_manager.raw(sql)
        db_wrapper.database.close()

    create_task_table()
    insert_task_record()

    response = client.get('/api/tasks/status/59cc0424-6f97-44c1-a253-7b4d7566e3f7',
                          json={}, headers=auth_header())
    json_data = response.get_json()

    assert 200 == response.status_code
    assert isinstance(json_data, dict)
    assert json_data.get('state')
    assert json_data.get('current')
    assert json_data.get('total')
    assert json_data.get('result')
