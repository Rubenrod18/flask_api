from datetime import datetime

import magic
from flask import url_for
from flask_security import verify_password
from marshmallow import fields, validate, pre_load, post_dump, ValidationError, validates
from werkzeug.exceptions import Forbidden, Unauthorized, NotFound, UnprocessableEntity, BadRequest

from app.extensions import ma
from app.models.role import Role as RoleModel
from app.models.user import User as UserModel
from app.utils import QUERY_OPERATORS, STRING_QUERY_OPERATORS
from config import Config


class Timestamp(fields.Field):
    """Field that serializes to timestamp integer and deserializes to a datetime.datetime class."""

    def _serialize(self, value, attr, obj, **kwargs):
        if not isinstance(value, datetime):
            return None
        return datetime.fromtimestamp(value.timestamp()).strftime('%Y-%m-%d %H:%M:%S')

    def _deserialize(self, value, attr, data, **kwargs):
        return datetime.timestamp(value)


class ExportWordInputSchema(ma.Schema):
    to_pdf = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def convert_to_integer(self, value, many, **kwargs):
        if 'to_pdf' in value:
            value['to_pdf'] = int(value.get('to_pdf'))
        return value


class GetDocumentDataInputSchema(ma.Schema):
    as_attachment = fields.Int(validate=validate.OneOf([1, 0]))

    @pre_load
    def convert_to_integer(self, value, many, **kwargs):
        if 'as_attachment' in value:
            value['as_attachment'] = int(value.get('as_attachment'))
        return value


class RoleSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id', 'name', 'description', 'label', 'created_at', 'updated_at',
            'deleted_at',
        )

    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    label = fields.Str()
    created_at = Timestamp()
    updated_at = Timestamp()
    deleted_at = Timestamp()

    @staticmethod
    def valid_request_role(data: dict) -> dict:
        if RoleModel.get_or_none(name=data.get('role_name')):
            raise BadRequest('Role name already created')

        return data


class UserSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id', 'name', 'last_name', 'email', 'genre', 'birth_date', 'active',
            'created_at', 'updated_at', 'deleted_at', 'created_by', 'roles',
        )

    id = fields.Int()
    created_by = fields.Nested(lambda: UserSchema(only=('id',)))
    name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    password = fields.Str(
        validate=validate.Length(min=Config.SECURITY_PASSWORD_LENGTH_MIN,
                                 max=50)
    )
    genre = fields.Str(validate=validate.OneOf(['m', 'f']))
    birth_date = fields.Date()
    active = fields.Bool()
    created_at = Timestamp()
    updated_at = Timestamp()
    deleted_at = Timestamp()
    roles = fields.List(fields.Nested(RoleSchema, only=('name', 'label')))

    def validate_credentials(self, data: dict) -> dict:
        self.validate_email(data)

        user = UserModel.get_or_none(email=data.get('email'))
        if user and not verify_password(data.get('password'), user.password):
            raise Unauthorized('Credentials invalid')

        return data

    @staticmethod
    def valid_request_user(data: dict) -> dict:
        if UserModel.get_or_none(email=data.get('email')):
            raise BadRequest('User email already created')

        return data

    @staticmethod
    def validate_password(password: str) -> None:
        password_length_min = Config.SECURITY_PASSWORD_LENGTH_MIN
        password_length_max = 50

        if len(password) < password_length_min:
            raise ValidationError(f'Password must be greater '
                                  f'than {password_length_min}.')
        if len(password) > password_length_max:
            raise ValidationError(f'Password must not be greater '
                                  f'than {password_length_max}.')

    @staticmethod
    def validate_email(data: dict) -> dict:
        user = UserModel.get_or_none(email=data.get('email'))

        if user is None:
            raise NotFound('User not found')

        if not user.active:
            raise Forbidden('User not actived')

        if user.deleted_at is not None:
            raise Forbidden('User deleted')

        return data


class DocumentSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id', 'name', 'mime_type', 'size', 'url', 'created_at',
            'updated_at', 'deleted_at', 'created_by', 'internal_filename'
        )

    id = fields.Int()
    created_by = fields.Nested('UserSchema', only=('id', 'name', 'last_name',
                                                   'email'))
    name = fields.Str()
    internal_filename = fields.Str()
    mime_type = fields.Str()
    directory_path = fields.Str()
    size = fields.Integer()
    created_at = Timestamp()
    updated_at = Timestamp()
    deleted_at = Timestamp()

    @post_dump()
    def make_url(self, data, **kwargs):
        data['url'] = url_for('documents_document_resource',
                              document_id=data['id'],
                              _external=True)
        return data

    @staticmethod
    def valid_request_file(data):
        is_valid_mime_type = (data.get('mime_type') in Config.ALLOWED_MIME_TYPES)

        file_content_type = magic.from_buffer(data.get('file_data'), mime=True)
        is_valid_file_content_type = (file_content_type in Config.ALLOWED_MIME_TYPES)

        if not is_valid_mime_type or not is_valid_file_content_type:
            raise UnprocessableEntity('mime_type not valid')

        return data


class _SearchValueSchema(ma.Schema):
    field_name = fields.Str()
    field_operator = fields.Str(validate=validate.OneOf(set(QUERY_OPERATORS + STRING_QUERY_OPERATORS)))
    field_value = fields.Raw()


class _SearchOrderSchema(ma.Schema):
    field_name = fields.Str()
    sorting = fields.Str(validate=validate.OneOf(['asc', 'desc']))


class SearchSchema(ma.Schema):
    search = fields.List(fields.Nested(_SearchValueSchema))
    order = fields.List(fields.Nested(_SearchOrderSchema))
    items_per_page = fields.Integer()
    page_number = fields.Integer()
