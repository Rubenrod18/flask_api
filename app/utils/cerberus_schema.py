def user_model_schema():
    """This is a cerberus schema for validating user field requests."""
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
        }
    }
