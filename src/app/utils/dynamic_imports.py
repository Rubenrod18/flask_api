import importlib


def get_attr_from_module(module: str, attr: str) -> any:
    """Get attribute from a module.

    Parameters
    ----------
    module : str
        Module absolute path.
    attr : str
        Module's attribute. It could be any kind of variable belongs to module.

    Examples
    --------

    >>> from app.utils.dynamic_imports import get_attr_from_module
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
