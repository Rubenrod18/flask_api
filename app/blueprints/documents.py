import logging
import mimetypes
import os
import uuid

from flask import Blueprint, request, current_app, send_file
from flask_login import current_user
from flask_security import roles_accepted
from marshmallow import EXCLUDE, ValidationError
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage
from werkzeug.exceptions import (NotFound, UnprocessableEntity,
                                 InternalServerError, BadRequest)

from app.blueprints.base import BaseResource
from app.extensions import api as root_api
from app.managers.document import DocumentManager
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
    doc_manager = DocumentManager()
    doc_serializer = DocumentSerializer()
    doc_attach_serializer = DocumentAttachmentSerializer()
    search_serializer = SearchSerializer()

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

    def get_doc_data(self, document_id: int) -> tuple:
        args = (DocumentModel.deleted_at.is_null(),)
        document = self.doc_manager.find(document_id, *args)
        if document is None:
            raise NotFound('Document doesn\'t exist')
        return {'data': self.doc_serializer.dump(document)}, 200

    def get_document_content(self, document_id: int):
        args = (DocumentModel.deleted_at.is_null(),)
        document = self.doc_manager.find(document_id, *args)
        if document is None:
            raise NotFound('Document doesn\'t exist')

        try:
            request_args = (self.doc_attach_serializer
                            .load(request.args.to_dict(), unknown=EXCLUDE))
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
        return send_file(**kwargs)


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
        try:
            data = self.doc_serializer.valid_request_file(
                self.get_request_file())
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
                'directory_path': current_app.config.get('STORAGE_DIRECTORY'),
                'size': fs.get_filesize(filepath),
            }
            document = self.doc_manager.create(**data)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.debug(e)
            raise InternalServerError()

        return {'data': self.doc_serializer.dump(document)}, 201


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
        if request.headers.get('Content-Type') == 'application/json':
            response = self.get_doc_data(document_id)
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
        document = self.doc_manager.find(document_id)
        if document is None:
            raise BadRequest('Document doesn\'t exist')

        if document.deleted_at is not None:
            raise BadRequest('Document already deleted')

        try:
            data = self.doc_serializer.valid_request_file(
                self.get_request_file())
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
            self.doc_manager.save(**data)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            logger.debug(e)
            raise InternalServerError()

        args = (DocumentModel.deleted_at.is_null(),)
        document = self.doc_manager.find(document_id, *args)
        return {'data': self.doc_serializer.dump(document)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 404: 'Not Found'},
             security='auth_token')
    @api.marshal_with(document_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def delete(self, document_id: int):
        document = self.doc_manager.find(document_id)
        if document is None:
            raise NotFound('Document doesn\'t exist')

        if document.deleted_at is not None:
            raise BadRequest('Document already deleted')

        document = self.doc_manager.delete(document_id)
        return {'data': self.doc_serializer.dump(document)}, 200


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
        try:
            request_data = self.search_serializer.load(request.get_json())
        except ValidationError as e:
            raise UnprocessableEntity(e.messages)

        doc_data = self.doc_manager.get(**request_data)
        doc_serializer = DocumentSerializer(many=True)

        return {
                   'data': doc_serializer.dump(list(doc_data['query'])),
                   'records_total': doc_data['records_total'],
                   'records_filtered': doc_data['records_filtered'],
               }, 200
