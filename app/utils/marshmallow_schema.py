from datetime import datetime

from flask import url_for
from marshmallow import fields, validate, pre_load, post_dump

from app.extensions import ma


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
        fields = ('id', 'name', 'description', 'label', 'created_at', 'updated_at', 'deleted_at')

    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    label = fields.Str()
    created_at = Timestamp()
    updated_at = Timestamp()
    deleted_at = Timestamp()


class UserSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = (
            'id', 'name', 'last_name', 'email', 'genre', 'birth_date', 'active', 'created_at', 'updated_at',
            'deleted_at', 'created_by', 'roles',
        )

    id = fields.Int()
    created_by = fields.Nested(lambda: UserSchema(only=('id',)))
    name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    password = fields.Str()
    genre = fields.Str(validate=validate.OneOf(['m', 'f']))
    birth_date = fields.Date()
    active = fields.Bool()
    created_at = Timestamp()
    updated_at = Timestamp()
    deleted_at = Timestamp()
    roles = fields.List(fields.Nested(RoleSchema, only=('name', 'label')))


class DocumentSchema(ma.Schema):
    class Meta:
        ordered = True
        fields = ('id', 'name', 'mime_type', 'size', 'url', 'created_at', 'updated_at', 'deleted_at', 'created_by')

    id = fields.Int()
    created_by = fields.Nested('UserSchema', only=('id',))
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
        data['url'] = url_for('documents_document_resource', document_id=data['id'], _external=True)
        return data
