"""Collection of functions and classes which make common patterns
shorter and easier."""

import importlib
from datetime import date, datetime

from flask import request


def get_attr_from_module(module: str, attr: str) -> any:
    """Get attribute from a module.

    Parameters
    ----------
    module : str
        Module absolute path.
    attr : str
        Module's attribute. It could be any kind of variable belongs
        to module.

    Examples
    --------

    >>> from app.utils import get_attr_from_module
    >>> module_path = 'app.blueprints.base'
    >>> module_attr = 'blueprint'
    >>> get_attr_from_module(module_path, module_attr)
    <flask.blueprints.Blueprint object at ...>

    Raises
    ------
    ImportError
        Module doesn't exist.
    AttributeError
        Attribute doesn't exist in module.

    """
    m = importlib.import_module(module)
    return getattr(m, attr)


def to_readable(obj: object) -> object:
    if obj is None or obj == '':
        return 'N/D'
    elif isinstance(obj, datetime):
        return obj.strftime('%Y/%m/%d %H:%M:%S')
    elif isinstance(obj, date):
        return obj.__str__()
    else:
        return obj


def pos_to_char(pos: int) -> str:
    return chr(pos + 97)


def find_longest_word(word_list: list) -> str:
    str_list = [str(item) for item in word_list]
    longest_word = max(str_list, key=len)
    return str(longest_word)


def ignore_keys(data: dict, exclude: list) -> dict:
    return dict({item: data[item] for item in data if item not in exclude})


def get_request_file(field_name: str = None) -> dict:
    field_name = 'document' if field_name is None else field_name
    file = {}
    request_file = request.files.to_dict().get(field_name)

    if request_file:
        file = {
            'mime_type': request_file.mimetype,
            'filename': request_file.filename,
            'file_data': request_file.read(),
        }
    return file


def filter_by_keys(data: dict, keys: list) -> dict:
    return {key: value for key, value in data.items() if key in keys}
