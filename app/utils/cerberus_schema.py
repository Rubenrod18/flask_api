from cerberus import Validator
from peewee import ModelBase

from app.models.user import User as UserModel
from app.utils import BIRTH_DATE_REGEX, EMAIL_REGEX, class_for_name


class MyValidator(Validator):
    def _validate_exists(self, exists, field, value):
        """Test if value of a field exists or not in database.

        The rule's arguments are validated against this schema:
        {'type': 'dict'}
        """
        module_name = exists.get('module_name')
        class_name = exists.get('class_name')
        model_field = exists.get('field_name')
        search_deleted = exists.get('search_deleted', False)
        exists_record_message = exists.get('exists_record_message', 'Already exists')
        no_exists_record_message = exists.get('no_exists_record_message', 'Already deleted')

        model = class_for_name(module_name, class_name)

        if isinstance(model, ModelBase):
            query_field = getattr(model, model_field)

            if search_deleted:
                query = model.get_or_none(query_field == value)
            else:
                query = (model.select()
                         .where(query_field == value, model.deleted_at.is_null(True))
                         .first())

            if query and exists_record_message:
                self._error(field, exists_record_message)
            elif not query and no_exists_record_message:
                self._error(field, no_exists_record_message)


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
            'exists': {
                'module_name': 'app.models.user',
                'class_name': 'User',
                'field_name': 'email',
                'no_exists_record_message': '',
                'search_deleted': True,
            },
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
                'exists_record_message': '',
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


def role_model_schema() -> dict:
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
    }


def user_login_schema() -> dict:
    """Cerberus schema for validating user login fields.

    :return: dict
    """
    return {
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
                'exists_record_message': '',
            },
        },
        'password': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'minlength': 5,
            'maxlength': 50,
        },
    }
