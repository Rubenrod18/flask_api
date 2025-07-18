from dependency_injector.wiring import inject, Provide
from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required
from flask_security import roles_accepted
from marshmallow import EXCLUDE
from werkzeug.datastructures import FileStorage as WerkzeugFileStorage

from app import serializers, swagger as swagger_models
from app.blueprints.base import BaseResource
from app.di_container import ServiceDIContainer
from app.extensions import api as root_api
from app.models.document import StorageTypes
from app.models.role import ROLES
from app.serializers.document import DocumentStorageTypeSerializer
from app.services.document import DocumentService

blueprint = Blueprint('documents', __name__)
api = root_api.namespace(
    'documents', description='Users with role admin, team_leader or worker can manage these endpoints.'
)


class BaseDocumentResource(BaseResource):
    @inject
    def __init__(
        self,
        rest_api: str,
        *args,
        service: DocumentService = Provide[ServiceDIContainer.document_service],
        **kwargs,
    ):
        super().__init__(rest_api, service, *args, **kwargs)


@api.route('')
class NewDocumentResource(BaseDocumentResource):
    parser = api.parser()
    parser.add_argument('Content-Type', type=str, location='headers', required=True, choices=('multipart/form-data',))
    parser.add_argument(
        'document',
        type=WerkzeugFileStorage,
        location='files',
        required=True,
    )
    parser.add_argument('storage_type', type=str, location='args', required=False, choices=StorageTypes.to_list())

    serializer_classes = {
        'document': serializers.DocumentSerializer,
        'document_storage_type': DocumentStorageTypeSerializer,
    }

    @jwt_required()
    @roles_accepted(*ROLES)
    @api.doc(responses={401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'}, security='auth_token')
    @api.expect(parser)
    @api.marshal_with(swagger_models.document_sw_model, envelope='data', code=201)
    def post(self) -> tuple:
        serializer = self.get_serializer(serializer_name='document')
        request_args = self.get_serializer(serializer_name='document_storage_type').load(
            request.args.to_dict(), unknown=EXCLUDE
        )
        validated_data = serializer.valid_request_file(self.get_request_file())
        validated_data.update(request_args)

        document = self.service.create(**validated_data)

        return serializer.dump(document), 201


@api.route('/<int:document_id>')
class DocumentResource(BaseDocumentResource):
    parser = api.parser()
    parser.add_argument(
        'accept',
        type=str,
        location='headers',
        required=True,
        choices=(
            'application/json',
            'application/octet-stream',
        ),
    )
    parser.add_argument('as_attachment', type=int, location='args', required=False, choices=(0, 1))

    serializer_classes = {
        'document': serializers.DocumentSerializer,
        'document_attachment': serializers.DocumentAttachmentSerializer,
    }

    @jwt_required()
    @roles_accepted(*ROLES)
    # NOTE: api.marshal_with cannot handle two differents kind of responses. That's the reason is not added here.
    @api.doc(
        responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.response(200, 'Success', swagger_models.document_sw_model)
    @api.expect(parser)
    def get(self, document_id: int) -> tuple:
        """Get Document data or download.

        - `Accept: application/json`: returns JSON data.
        - `Accept: application/octet-stream`: returns the content of the document.

        """
        serializer = self.get_serializer(serializer_name='document')
        serializer.load({'id': document_id}, partial=True)

        if request.headers.get('Accept') == 'application/octet-stream':
            request_args = self.get_serializer(serializer_name='document_attachment').load(
                request.args.to_dict(), unknown=EXCLUDE
            )
            response = send_file(**self.service.get_document_content(document_id, request_args))
        else:
            document = self.service.find_by_id(document_id)
            response = serializer.dump(document), 200

        return response

    @jwt_required()
    @roles_accepted(*ROLES)
    @api.doc(
        responses={401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(parser)
    @api.marshal_with(swagger_models.document_sw_model, envelope='data')
    def put(self, document_id: int) -> tuple:
        serializer = self.get_serializer(serializer_name='document')
        serializer.load({'id': document_id}, partial=True)
        validated_data = serializer.valid_request_file(self.get_request_file())

        document = self.service.save(document_id, **validated_data)

        return serializer.dump(document), 200

    @jwt_required()
    @roles_accepted(*ROLES)
    @api.doc(
        responses={400: 'Bad Request', 401: 'Unauthorized', 403: 'Forbidden', 404: 'Not Found'}, security='auth_token'
    )
    @api.marshal_with(swagger_models.document_sw_model, envelope='data')
    def delete(self, document_id: int) -> tuple:
        serializer = self.get_serializer(serializer_name='document')
        serializer.load({'id': document_id}, partial=True)

        document = self.service.delete(document_id)

        return serializer.dump(document), 200


@api.route('/search')
class SearchDocumentResource(BaseDocumentResource):
    serializer_classes = {'document': serializers.DocumentSerializer, 'search': serializers.SearchSerializer}

    @jwt_required()
    @roles_accepted(*ROLES)
    @api.doc(
        responses={200: 'Success', 401: 'Unauthorized', 403: 'Forbidden', 422: 'Unprocessable Entity'},
        security='auth_token',
    )
    @api.expect(swagger_models.search_input_sw_model)
    @api.marshal_with(swagger_models.document_search_output_sw_model)
    def post(self) -> tuple:
        serializer = self.get_serializer(serializer_name='document', many=True)
        validated_data = self.get_serializer(serializer_name='search').load(request.get_json())

        doc_data = self.service.get(**validated_data)

        return {
            'data': serializer.dump(list(doc_data['query'])),
            'records_total': doc_data['records_total'],
            'records_filtered': doc_data['records_filtered'],
        }, 200
