from cerberus import Validator

from app.models.user import User as UserModel
from app.utils import BIRTH_DATE_REGEX, EMAIL_REGEX, class_for_name

PASSWORD_SCHEMA = {
    'password': {
        'type': 'string',
        'required': True,
        'empty': False,
        'nullable': False,
        'minlength': 5,
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
        message = 'Doesn\'t exists in database'

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
        message = 'Already exists'

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
                        'allowed': allowed_fields,
                    },
                    'field_value': {
                        'type': ['string', 'integer'],
                    }
                },
            },
        },
        'order': {
            'type': 'string',
            'required': False,
            'empty': False,
            'nullable': False,
            'allowed': ['asc', 'desc'],
        },
        'sort': {
            'type': 'string',
            'required': False,
            'empty': False,
            'nullable': False,
            'allowed': UserModel.get_fields(['password']),
        },
        'items_per_page': {
            'type': 'integer',
            'required': False,
            'empty': False,
            'nullable': False,
            'min': 1,
        },
        'page_number': {
            'type': 'integer',
            'required': False,
            'empty': False,
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
            'required': True,
            'empty': False,
            'nullable': False,
            'maxlength': 255,
        },
        'description': {
            'type': 'string',
            'required': False,
            'empty': True,
            'nullable': True,
            'maxlength': 255,
        },
        'slug': {
            'type': 'string',
            'required': is_creation,
            'empty': False if is_creation else False,
            'nullable': False if is_creation else False,
            'maxlength': 255,
            'no_exists': {
                'module_name': 'app.models.role',
                'class_name': 'Role',
                'field_name': 'slug',
                'only_deleted': False,
            },
        }
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

    schema.update(PASSWORD_SCHEMA)

    return schema


def confirm_reset_password_schema() -> dict:
    return PASSWORD_SCHEMA
