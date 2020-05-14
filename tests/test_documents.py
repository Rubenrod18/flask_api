from urllib.parse import urlparse

from flask import current_app
from flask.testing import FlaskClient
from peewee import fn

from app.extensions import db_wrapper
from app.models.document import Document as DocumentModel
from app.utils.file_storage import FileStorage


def test_save_document(client: FlaskClient, auth_header: any):
    pdf_file = '%s/example.pdf' % current_app.config.get('STORAGE_DIRECTORY')
    data = {
        'document': open(pdf_file, 'rb'),
    }

    response = client.post('/documents', data=data, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    parse_url = urlparse(json_data.get('url'))

    assert 200 == response.status_code
    assert 1 == json_data.get('created_by')
    assert pdf_file == json_data.get('name')
    assert 'application/pdf' == json_data.get('mime_type')
    assert FileStorage.get_filesize(pdf_file) == json_data.get('size')
    assert parse_url.scheme and parse_url.netloc
    assert json_data.get('created_at')
    assert json_data.get('updated_at') == json_data.get('created_at')
    assert json_data.get('deleted_at') is None


def test_update_document(client: FlaskClient, auth_header: any):
    pdf_file = '%s/example.pdf' % current_app.config.get('STORAGE_DIRECTORY')
    document = (DocumentModel.select()
                   .where(DocumentModel.deleted_at.is_null())
                   .order_by(fn.Random())
                   .limit(1)
                   .get())
    document_id = document.id

    data = {
        'document': open(pdf_file, 'rb'),
    }

    response = client.put(f'/documents/{document_id}', data=data, headers=auth_header())
    json_response = response.get_json()
    json_data = json_response.get('data')

    parse_url = urlparse(json_data.get('url'))

    assert 200 == response.status_code
    assert isinstance(json_data.get('created_by'), int)
    assert pdf_file == json_data.get('name')
    assert document.mime_type == json_data.get('mime_type')
    assert FileStorage.get_filesize(pdf_file) == json_data.get('size')
    assert parse_url.scheme and parse_url.netloc
    assert document.created_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('created_at')
    assert json_data.get('updated_at') > json_data.get('created_at')
    assert json_data.get('deleted_at') is None


def test_get_document_data(client: FlaskClient, auth_header: any):
    document = (DocumentModel.select()
                   .where(DocumentModel.deleted_at.is_null())
                   .order_by(fn.Random())
                   .limit(1)
                   .get())
    document_id = document.id

    headers = auth_header()
    headers['Content-Type'] = 'application/json'

    response = client.get(f'/documents/{document_id}', headers=headers)
    json_response = response.get_json()
    json_data = json_response.get('data')

    parse_url = urlparse(json_data.get('url'))

    assert 200 == response.status_code
    assert document.created_by.id == json_data.get('created_by')
    assert document.name == json_data.get('name')
    assert document.mime_type == json_data.get('mime_type')
    assert document.size == json_data.get('size')
    assert parse_url.scheme and parse_url.netloc
    assert document.created_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('created_at')
    assert document.updated_at.strftime('%Y-%m-%d %H:%m:%S') == json_data.get('updated_at')
    assert document.deleted_at == json_data.get('deleted_at')


def test_get_document_file(client: FlaskClient, auth_header: any):
    document = (DocumentModel.select()
                .where(DocumentModel.deleted_at.is_null())
                .order_by(fn.Random())
                .limit(1)
                .get())
    document_id = document.id

    response = client.get(f'/documents/{document_id}', headers=auth_header())

    assert isinstance(response.get_data(), bytes)


def test_delete_document(client: FlaskClient, auth_header: any):
    document_id = (DocumentModel.select(DocumentModel.id)
                   .where(DocumentModel.deleted_at.is_null())
                   .order_by(fn.Random())
                   .limit(1)
                   .get()
                   .id)
    db_wrapper.database.close()

    response = client.delete('/documents/%s' % document_id, headers=auth_header())

    json_response = response.get_json()
    json_data = json_response.get('data')

    print(json_data)

    assert 200 == response.status_code
    assert document_id == json_data.get('id')
    assert json_data.get('deleted_at') is not None
    assert json_data.get('deleted_at') >= json_data.get('updated_at')


def test_search_document(client: FlaskClient, auth_header: any):
    document_name = (DocumentModel.select(DocumentModel.name)
                 .where(DocumentModel.deleted_at.is_null())
                 .order_by(fn.Random())
                 .limit(1)
                 .get()
                 .name)
    db_wrapper.database.close()

    json_body = {
        'search': [
            {
                'field_name': 'name',
                'field_value': document_name,
            }
        ],
        'order': 'desc',
        'sort': 'id',
    }

    response = client.post('/documents/search', json=json_body, headers=auth_header())

    json_response = response.get_json()

    document_data = json_response.get('data')
    records_total = json_response.get('records_total')
    records_filtered = json_response.get('records_filtered')

    assert 200 == response.status_code
    assert isinstance(document_data, list)
    assert records_total > 0
    assert records_filtered > 0 and records_filtered <= records_total
    assert document_data[0]['name'].find(document_name) != -1