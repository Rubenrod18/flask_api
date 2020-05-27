import logging
import mimetypes
import os
import uuid
from datetime import datetime

from flask import Blueprint, request, current_app, send_file
from flask_login import current_user
from flask_restful import Api, reqparse
from flask_security import roles_accepted
from werkzeug.exceptions import NotFound, UnprocessableEntity, InternalServerError, BadRequest

from app.blueprints.base import BaseResource
from app.models.document import Document as DocumentModel
from app.utils.cerberus_schema import MyValidator, document_save_model_schema, document_update_model_schema, \
    search_model_schema
from app.utils.decorators import token_required
from app.utils.file_storage import FileStorage

blueprint = Blueprint('documents', __name__, url_prefix='/documents')
api = Api(blueprint)

logger = logging.getLogger(__name__)


class DocumentResource(BaseResource):
    db_model = DocumentModel
    field_name = 'document'

    def get_request_file(self) -> dict:
        file = {}
        files = request.files.to_dict()
        request_file = files.get(self.field_name)

        if files and request_file:
            file = {
                self.field_name: {
                    'mime_type': request_file.mimetype,
                    'filename': request_file.filename,
                    'file': request_file.read(),
                },
            }

        return file

    def get_document_data(self, document_id: int) -> tuple:
        document = DocumentModel.get_or_none(DocumentModel.id == document_id,
                                             DocumentModel.deleted_at.is_null())

        if isinstance(document, DocumentModel):
            document_dict = document.serialize()
        else:
            raise NotFound('Document doesn\'t exist')

        return {
                   'data': document_dict,
               }, 200

    def get_document_content(self, document_id: int):
        document = DocumentModel.get_or_none(DocumentModel.id == document_id,
                                             DocumentModel.deleted_at.is_null())

        if isinstance(document, DocumentModel):
            # TODO: RequestParse will be deprecated in the future. Replace RequestParse to marshmallow
            # https://flask-restful.readthedocs.io/en/latest/reqparse.html
            parser = reqparse.RequestParser()
            parser.add_argument('as_attachment', type=int, location='args')

            args = parser.parse_args()
            as_attachment = args.get('as_attachment') or 0

            mime_type = document.mime_type
            file_extension = mimetypes.guess_extension(mime_type)

            attachment_filename = document.name if document.name.find(
                file_extension) else f'{document.name}{file_extension}'

            kwargs = {
                'filename_or_fp': document.get_filepath(),
                'mimetype': mime_type,
                'as_attachment': as_attachment,
            }

            if as_attachment:
                kwargs['attachment_filename'] = attachment_filename

            response = send_file(**kwargs)
        else:
            raise NotFound('Document doesn\'t exist')

        return response


@api.resource('')
class NewDocumentResource(DocumentResource):
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self):
        request_data = self.get_request_file()

        v = MyValidator(schema=document_save_model_schema())
        if not v.validate(request_data):
            raise UnprocessableEntity(v.errors)

        request_file = request_data.get(self.field_name)
        file_extension = mimetypes.guess_extension(request_file.get('mime_type'))

        internal_filename = '%s%s' % (uuid.uuid1().hex, file_extension)
        filepath = '%s/%s' % (current_app.config.get('STORAGE_DIRECTORY'), internal_filename)

        try:
            fs = FileStorage()
            fs.save_bytes(request_file.get('file'), filepath)

            data = {
                'created_by': current_user.id,
                'name': request_file.get('filename'),
                'internal_filename': internal_filename,
                'mime_type': request_file.get('mime_type'),
                'directory_path': filepath,
                'size': fs.get_filesize(filepath),
            }

            document = DocumentModel.create(**data)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.debug(e)
            raise InternalServerError()

        document_dict = document.serialize()

        return {
                   'data': document_dict,
               }, 200


@api.resource('/<int:document_id>')
class DocumentResource(DocumentResource):
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def get(self, document_id: int) -> tuple:
        headers = request.headers.get('Content-Type')

        if headers == 'application/json':
            response = self.get_document_data(document_id)
        else:
            response = self.get_document_content(document_id)

        return response

    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def put(self, document_id: int) -> tuple:
        request_data = self.get_request_file()
        request_data['id'] = document_id

        v = MyValidator(schema=document_update_model_schema())
        if not v.validate(request_data):
            raise UnprocessableEntity(v.errors)

        document = DocumentModel.get(id=document_id)

        request_file = request_data.get(self.field_name)
        filepath = f'{document.directory_path}/{document.internal_filename}'

        try:
            fs = FileStorage()
            fs.save_bytes(request_file.get('file'), filepath, override=True)

            data = {
                'name': request_file.get('filename'),
                'mime_type': request_file.get('mime_type'),
                'size': fs.get_filesize(filepath),
                'id': document_id,
            }

            DocumentModel(**data).save()
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.debug(e)
            raise InternalServerError()

        document = (DocumentModel.get_or_none(DocumentModel.id == document_id,
                                              DocumentModel.deleted_at.is_null()))
        document_dict = document.serialize()

        return {
                   'data': document_dict,
               }, 200

    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def delete(self, document_id: int):
        document = DocumentModel.get_or_none(DocumentModel.id == document_id)

        if isinstance(document, DocumentModel):
            if document.deleted_at is None:
                document.deleted_at = datetime.utcnow()
                document.save()

                document_dict = document.serialize()
            else:
                raise BadRequest('Document already deleted')
        else:
            raise NotFound('Document doesn\'t exist')

        return {
                   'data': document_dict,
               }, 200


@api.resource('/search')
class SearchDocumentResource(DocumentResource):
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self):
        data = request.get_json()

        document_fields = DocumentModel.get_fields(['password'])
        v = MyValidator(schema=search_model_schema(document_fields))
        v.allow_unknown = False

        if not v.validate(data):
            return UnprocessableEntity(v.errors)

        page_number, items_per_page, order_by = self.get_request_query_fields(data)

        query = DocumentModel.select()
        records_total = query.count()

        query = self.create_search_query(query, data)

        query = (query.order_by(*order_by)
                 .paginate(page_number, items_per_page))

        records_filtered = query.count()
        document_list = []

        for document in query:
            document_dict = document.serialize()
            document_list.append(document_dict)

        return {
                   'data': document_list,
                   'records_total': records_total,
                   'records_filtered': records_filtered,
               }, 200
