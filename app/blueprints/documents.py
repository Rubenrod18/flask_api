import logging
import mimetypes
import os
import uuid
from datetime import datetime

from flask import Blueprint, request, current_app, send_file
from flask_login import current_user
from flask_security import roles_accepted
from marshmallow import EXCLUDE, ValidationError
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage
from werkzeug.exceptions import (NotFound, UnprocessableEntity,
                                 InternalServerError, BadRequest)

from app.blueprints.base import BaseResource
from app.extensions import api as root_api
from app.models.document import Document as DocumentModel
from app.serializers import (DocumentSerializer, DocumentAttachmentSerializer,
                             SearchSerializer)
from app.swagger import (document_output_sw_model,
                         document_search_output_sw_model, search_input_sw_model)
from app.utils.decorators import token_required
from app.utils.file_storage import FileStorage

_API_DESCRIPTION = ('Users with role admin, team_leader or worker can '
                    'manage these endpoints.')

blueprint = Blueprint('documents', __name__)
api = root_api.namespace('documents', description=_API_DESCRIPTION)
logger = logging.getLogger(__name__)


class DocumentBaseResource(BaseResource):
    db_model = DocumentModel
    request_field_name = 'document'
    document_serializer = DocumentSerializer()

    def get_request_file(self) -> dict:
        file = {}
        files = request.files.to_dict()
        request_file = files.get(self.request_field_name)

        if files and request_file:
            file = {
                'mime_type': request_file.mimetype,
                'filename': request_file.filename,
                'file_data': request_file.read(),
            }

        return file

    def get_document_data(self, document_id: int) -> tuple:
        document = DocumentModel.get_or_none(DocumentModel.id == document_id,
                                             DocumentModel.deleted_at.is_null())
        if document is None:
            raise NotFound('Document doesn\'t exist')

        document_data = self.document_serializer.dump(document)

        return {'data': document_data}, 200

    @staticmethod
    def get_document_content(document_id: int):
        document = DocumentModel.get_or_none(DocumentModel.id == document_id,
                                             DocumentModel.deleted_at.is_null())
        if document is None:
            raise NotFound('Document doesn\'t exist')

        try:
            serializer = DocumentAttachmentSerializer()
            request_args = serializer.load(request.args.to_dict(),
                                           unknown=EXCLUDE)
            as_attachment = request_args.get('as_attachment', 0)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

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

        return response


@api.route('')
class NewDocumentResource(DocumentBaseResource):
    parser = api.parser()
    parser.add_argument('Content-Type', type=str, location='headers',
                        required=True, choices=('multipart/form-data',))
    parser.add_argument(DocumentBaseResource.request_field_name,
                        type=WerkzeugFileStorage, location='files',
                        required=True, help='You only can upload Excel and '
                                            'PDF files.')

    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(parser)
    @api.marshal_with(document_output_sw_model, code=201)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self):
        request_data = self.get_request_file()

        try:
            data = self.document_serializer.valid_request_file(request_data)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        file_extension = mimetypes.guess_extension(data.get('mime_type'))
        internal_filename = '%s%s' % (uuid.uuid1().hex, file_extension)
        filepath = '%s/%s' % (
            current_app.config.get('STORAGE_DIRECTORY'), internal_filename
        )

        try:
            fs = FileStorage()
            fs.save_bytes(data.get('file_data'), filepath)

            data = {
                'created_by': current_user.id,
                'name': data.get('filename'),
                'internal_filename': internal_filename,
                'mime_type': data.get('mime_type'),
                'directory_path': filepath,
                'size': fs.get_filesize(filepath),
            }

            document = DocumentModel.create(**data)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.debug(e)
            raise InternalServerError()

        document_data = self.document_serializer.dump(document)

        return {'data': document_data}, 201


@api.route('/<int:document_id>')
class DocumentResource(DocumentBaseResource):
    _parser = api.parser()
    _parser.add_argument('Content-Type', type=str, location='headers',
                         required=True, choices=('application/json',
                                                 'application/octet-stream',))

    @api.doc(responses={200: ('Success', document_output_sw_model),
                        401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(_parser)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def get(self, document_id: int) -> tuple:
        headers = request.headers.get('Content-Type')

        if headers == 'application/json':
            response = self.get_document_data(document_id)
        else:
            response = self.get_document_content(document_id)

        return response

    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(NewDocumentResource.parser)
    @api.marshal_with(document_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def put(self, document_id: int) -> tuple:
        document = DocumentModel.get_or_none(DocumentModel.id == document_id)
        if document is None:
            raise BadRequest('Document doesn\'t exist')

        if document.deleted_at is not None:
            raise BadRequest('Document already deleted')

        request_data = self.get_request_file()
        try:
            data = self.document_serializer.valid_request_file(request_data)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        filepath = f'{document.directory_path}/{document.internal_filename}'

        try:
            fs = FileStorage()
            fs.save_bytes(data.get('file_data'), filepath, override=True)

            data = {
                'name': data.get('filename'),
                'mime_type': data.get('mime_type'),
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
        document_data = self.document_serializer.dump(document)

        return {'data': document_data}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 404: 'Not Found'},
             security='auth_token')
    @api.marshal_with(document_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def delete(self, document_id: int):
        document = DocumentModel.get_or_none(DocumentModel.id == document_id)
        if document is None:
            raise NotFound('Document doesn\'t exist')

        if document.deleted_at is not None:
            raise BadRequest('Document already deleted')

        document.deleted_at = datetime.utcnow()
        document.save()

        document_data = self.document_serializer.dump(document)

        return {'data': document_data}, 200


@api.route('/search')
class SearchDocumentResource(DocumentBaseResource):
    @api.doc(responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(search_input_sw_model)
    @api.marshal_with(document_search_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def post(self):
        request_data = request.get_json()
        try:
            data = SearchSerializer().load(request_data)
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        page_number, items_per_page, order_by = self.get_request_query_fields(data)

        query = DocumentModel.select()
        records_total = query.count()

        query = self.create_search_query(query, request_data)
        query = (query.order_by(*order_by)
                 .paginate(page_number, items_per_page))

        records_filtered = query.count()
        self.document_serializer = DocumentSerializer(many=True)
        document_data = self.document_serializer.dump(list(query))

        return {
                   'data': document_data,
                   'records_total': records_total,
                   'records_filtered': records_filtered,
               }, 200
