from app.celery.tests.tasks import create_task_table, insert_task_record
from app.extensions import db, db_wrapper
from tests.custom_flask_client import CustomFlaskClient


def _create_task_record():
    create_task_table()
    insert_task_record()


def test_check_task_status(client: CustomFlaskClient, auth_header: any):
    # TODO: This will fail until will be migrated to MySQL
    _create_task_record()

    task_id = '59cc0424-6f97-44c1-a253-7b4d7566e3f7'
    response = client.get(f'/api/tasks/status/{task_id}', json={},
                          headers=auth_header())
    json_data = response.get_json()

    assert 200 == response.status_code
    assert isinstance(json_data, dict)
    assert json_data.get('state')
    assert json_data.get('current')
    assert json_data.get('total')
    assert json_data.get('result')
