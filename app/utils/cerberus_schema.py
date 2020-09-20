import magic
from cerberus import Validator
from flask import current_app

from app.utils import BIRTH_DATE_REGEX, EMAIL_REGEX, class_for_name, QUERY_OPERATORS, STRING_QUERY_OPERATORS


def get_password_schema() -> dict:
    return {
        'password': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'minlength': current_app.config.get('SECURITY_PASSWORD_LENGTH_MIN'),
            'maxlength': 50,
        },
    }


class MyValidator(Validator):
    def _validate_exists(self, exists, field, value):
        """Test if value of a value exists in database.

        The rule's arguments are validated against this schema:
        {'type': 'dict'}
        """
        module_name = exists.get('module_name')
        class_name = exists.get('class_name')
        model_field = exists.get('field_name')
        only_deleted = exists.get('only_deleted', False)
        message = exists.get('message', f'{value} doesn\'t exists in database')

        model = class_for_name(module_name, class_name)
        query_field = getattr(model, model_field)
        query = model.select()

        if only_deleted:
            query = query.where(query_field == value, model.deleted_at.is_null(False))
        else:
            query = query.where(query_field == value)

        row = query.first()

        if not row:
            self._error(field, message)

    def _validate_no_exists(self, exists, field, value):
        """Test if value of a value doesn't exists in database.

        The rule's arguments are validated against this schema:
        {'type': 'dict'}
        """
        module_name = exists.get('module_name')
        class_name = exists.get('class_name')
        model_field = exists.get('field_name')
        only_deleted = exists.get('only_deleted', False)
        message = exists.get('message', f'{value} already exists')

        model = class_for_name(module_name, class_name)
        query_field = getattr(model, model_field)
        query = model.select()

        if only_deleted:
            query = query.where(query_field == value, model.deleted_at.is_null(False))
        else:
            query = query.where(query_field == value)

        row = query.first()

        if row:
            self._error(field, message)

    def _validate_valid_mime_type(self, mime_types, field, value):
        """Test if a request file is valid.

        The rule's arguments are validated against this schema:
        {'type': 'list'}
        """
        file_content_type = magic.from_buffer(value, mime=True)

        if not file_content_type in mime_types:
            self._error(field, 'file invalid')


def user_model_schema(is_creation: bool = True) -> dict:
    """Cerberus schema for validating user fields.

    :return: dict
    """

    return {
        'name': {
            'type': 'string',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'maxlength': 255,
        },
        'last_name': {
            'type': 'string',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'maxlength': 255,
        },
        'email': {
            'type': 'string',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'regex': EMAIL_REGEX,
            'no_exists': {
                'module_name': 'app.models.user',
                'class_name': 'User',
                'field_name': 'email',
                'only_deleted': False,
            },
        },
        'genre': {
            'type': 'string',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'allowed': ['m', 'f'],
        },
        'password': {
            'type': 'string',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'minlength': 5,
            'maxlength': 50,
        },
        'birth_date': {
            'type': 'string',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'regex': BIRTH_DATE_REGEX,
        },
        'role_id': {
            'type': 'integer',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'exists': {
                'module_name': 'app.models.role',
                'class_name': 'Role',
                'field_name': 'id',
                'only_deleted': False,
            },
        },
    }


def search_model_schema(allowed_fields: set) -> dict:
    """Cerberus schema for search fields such as: items_per_page, page_number, etc.

    :return: dict
    """
    return {
        'search': {
            'type': 'list',
            'required': False,
            'empty': True,
            'nullable': False,
            'maxlength': 255,
            'schema': {
                'type': 'dict',
                'schema': {
                    'field_name': {
                        'type': 'string',
                        'required': True,
                        'empty': False,
                        'nullable': False,
                        'maxlength': 255,
                        'allowed': allowed_fields,
                    },
                    'field_operator': {
                        'type': 'string',
                        'required': True,
                        'empty': False,
                        'nullable': False,
                        'maxlength': 255,
                        'allowed': QUERY_OPERATORS + STRING_QUERY_OPERATORS,
                    },
                    'field_value': {
                        'type': ['string', 'integer'],
                        'required': True,
                        'empty': True,
                        'maxlength': 255,
                        'nullable': False,
                    },
                },
            },
        },
        'order': {
            'type': 'list',
            'required': False,
            'empty': True,
            'nullable': False,
            'maxlength': 255,
            'schema': {
                'type': 'list',
                'required': True,
                'items': [
                    {
                        'type': 'string',
                        'required': True,
                        'empty': False,
                        'nullable': False,
                        'allowed': allowed_fields,
                    },
                    {
                        'type': 'string',
                        'required': True,
                        'empty': False,
                        'nullable': False,
                        'allowed': ['asc', 'desc'],
                    }
                ]
            }
        },
        'items_per_page': {
            'type': 'integer',
            'required': False,
            'empty': True,
            'nullable': False,
            'min': 1,
        },
        'page_number': {
            'type': 'integer',
            'required': False,
            'empty': True,
            'nullable': False,
            'min': 1,
        },
    }


def role_model_schema(is_creation: bool = True) -> dict:
    """Cerberus schema for validating role fields.

    :return: dict
    """
    return {
        'name': {
            'type': 'string',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'maxlength': 255,
            'no_exists': {
                'module_name': 'app.models.role',
                'class_name': 'Role',
                'field_name': 'name',
                'only_deleted': False,
            },
        },
        'description': {
            'type': 'string',
            'required': False,
            'empty': True,
            'nullable': True,
            'maxlength': 255,
        },
        'label': {
            'type': 'string',
            'required': is_creation,
            'empty': False,
            'nullable': False,
            'maxlength': 255,
        },
    }


def user_login_schema() -> dict:
    """Cerberus schema for validating user login fields.

    :return: dict
    """
    schema = {
        'email': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'regex': EMAIL_REGEX,
            'exists': {
                'module_name': 'app.models.user',
                'class_name': 'User',
                'field_name': 'email',
            },
        },
    }

    schema.update(get_password_schema())

    return schema


def confirm_reset_password_schema() -> dict:
    return get_password_schema()


def document_model_schema() -> dict:
    return {
        'document': {
            'type': 'dict',
            'required': True,
            'empty': False,
            'nullable': False,
            'schema': {
                'mime_type': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                    'nullable': False,
                    'allowed': list(current_app.config.get('ALLOWED_MIME_TYPES')),
                },
                'filename': {
                    'type': 'string',
                    'required': True,
                    'empty': False,
                    'nullable': False,
                },
                'file': {
                    'type': 'binary',
                    'required': True,
                    'empty': False,
                    'nullable': False,
                    'valid_mime_type': list(current_app.config.get('ALLOWED_MIME_TYPES')),
                },
            },
        },
    }
