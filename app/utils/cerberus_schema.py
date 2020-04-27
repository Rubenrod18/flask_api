from app.models.role import Role as RoleModel
from app.models.user import User as UserModel


def user_model_schema() -> dict:
    """Cerberus schema for validating user fields.

    :return: dict
    """
    query = (RoleModel.select(RoleModel.id)
                     .where(RoleModel.deleted_at.is_null(False)))
    deleted_role_ids = [item.id for item in query]

    return {
        'name': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'maxlength': 255,
        },
        'last_name': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'maxlength': 255,
        },
        'age': {
            'type': 'integer',
            'required': True,
            'empty': False,
            'nullable': False,
            'min': 0,
            'max': 100,
        },
        'birth_date': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'regex': r'^(19[0-9]{2}|2[0-9]{3})'  # Year
                     r'-(0[1-9]|1[012])'  # Month
                     r'-([123]0|[012][1-9]|31)$',  # Day
        },
        'role_id': {
            'type': 'integer',
            'required': True,
            'empty': False,
            'nullable': False,
            'forbidden': deleted_role_ids,
        }
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
            'allowed': UserModel.get_fields(),
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
    }