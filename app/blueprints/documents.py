from flask import Blueprint, request
from flask_security import roles_accepted
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage

from app.blueprints.base import BaseResource
from app.extensions import api as root_api
from app.serializers import DocumentSerializer
from app.services.document import DocumentService
from app.swagger import (document_output_sw_model,
                         document_search_output_sw_model, search_input_sw_model)
from app.utils import get_request_file
from app.utils.decorators import token_required

_API_DESCRIPTION = ('Users with role admin, team_leader or worker can '
                    'manage these endpoints.')

blueprint = Blueprint('documents', __name__)
api = root_api.namespace('documents', description=_API_DESCRIPTION)


class DocumentBaseResource(BaseResource):
    doc_service = DocumentService()
    doc_serializer = DocumentSerializer()


@api.route('')
class NewDocumentResource(DocumentBaseResource):
    parser = api.parser()
    parser.add_argument('Content-Type', type=str, location='headers',
                        required=True, choices=('multipart/form-data',))
    parser.add_argument('document', type=WerkzeugFileStorage, location='files',
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
        document = self.doc_service.create(**get_request_file())
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
            document = self.doc_service.find(document_id)
            response = {'data': self.doc_serializer.dump(document)}, 200
        else:
            args = request.args.to_dict()
            response = self.doc_service.get_document_content(document_id,
                                                             **args)
        return response

    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found',
                        422: 'Unprocessable Entity'},
             security='auth_token')
    @api.expect(NewDocumentResource.parser)
    @api.marshal_with(document_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def put(self, document_id: int) -> tuple:
        document = self.doc_service.save(document_id)
        return {'data': self.doc_serializer.dump(document)}, 200

    @api.doc(responses={400: 'Bad Request', 401: 'Unauthorized',
                        403: 'Forbidden', 404: 'Not Found'},
             security='auth_token')
    @api.marshal_with(document_output_sw_model)
    @token_required
    @roles_accepted('admin', 'team_leader', 'worker')
    def delete(self, document_id: int):
        document = self.doc_service.delete(document_id)
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
        doc_data = self.doc_service.get(**request.get_json())
        doc_serializer = DocumentSerializer(many=True)
        return {
                   'data': doc_serializer.dump(list(doc_data['query'])),
                   'records_total': doc_data['records_total'],
                   'records_filtered': doc_data['records_filtered'],
               }, 200
