from app.models.user import User as UserModel


def user_model_schema() -> dict:
    """Cerberus schema for validating user fields.

    :return: dict
    """
    return {
        'name': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'maxlength': 255
        },
        'last_name': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'maxlength': 255
        },
        'age': {
            'type': 'integer',
            'required': True,
            'empty': False,
            'nullable': False,
            'min': 0,
            'max': 100
        },
        'birth_date': {
            'type': 'string',
            'required': True,
            'empty': False,
            'nullable': False,
            'regex': r'^(19[0-9]{2}|2[0-9]{3})'  # Year
                     r'-(0[1-9]|1[012])'  # Month
                     r'-([123]0|[012][1-9]|31)$'  # Day
        },
    }


def search_model_schema() -> dict:
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
                        'allowed': UserModel.get_fields(['id'])
                    },
                    'field_value': {
                        'type': ['string', 'integer']
                    }
                }
            }
        },
        'order': {
            'type': 'string',
            'required': False,
            'empty': False,
            'nullable': False,
            'allowed': ['asc', 'desc']
        },
        'sort': {
            'type': 'string',
            'required': False,
            'empty': False,
            'nullable': False,
            'allowed': UserModel.get_fields()
        },
        'items_per_page': {
            'type': 'integer',
            'required': False,
            'empty': False,
            'nullable': False,
            'min': 1
        },
        'page_number': {
            'type': 'integer',
            'required': False,
            'empty': False,
            'nullable': False,
            'min': 1
        },
    }
