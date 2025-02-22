import importlib
import logging

logger = logging.getLogger(__name__)


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


def exists_attr_in_module(module: str, attr: str) -> bool:
    """Check if an attribute exists in a module.

    Parameters
    ----------
    module : str
        Module absolute path.
    attr : str
        Module's attribute. It could be any kind of variable belongs
        to module.

    Returns
    -------
    bool
        True if exists, otherwise False.

    Example
    -------
    >>> from app.utils.dynamic_imports import exists_attr_in_module
    >>> module_path = 'app.blueprints.base'
    >>> module_attr = 'blueprint'
    >>> exists_attr_in_module(module_path, module_attr)
    True

    """
    exists = False
    try:
        attr = get_attr_from_module(module, attr)
        if attr:
            exists = True
    except (ImportError, AttributeError) as e:
        logger.warning(e)
        exists = False

    return exists
