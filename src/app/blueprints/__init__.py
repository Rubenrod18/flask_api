"""Registers Flask blueprints."""

import os

from app.utils.dynamic_imports import get_attr_from_module


def get_blueprints() -> list:
    """Get Blueprints via dynamic way."""

    def get_bp_modules() -> list:
        """Get Blueprints modules."""
        abs_path = os.path.abspath(__file__)
        path = os.path.dirname(abs_path)
        dirs = os.listdir(path)

        dirs.remove(os.path.basename(__file__))

        return dirs

    def get_bp_instances(modules: list) -> list:
        """Get Blueprints instances."""
        blueprints = []
        modules.sort()

        for item in modules:
            if item.endswith('.py'):
                abs_path_module = f'{__name__}.{item[:-3]}'
                bp = get_attr_from_module(abs_path_module, 'blueprint')
                blueprints.append(bp)

        return blueprints

    bp_modules = get_bp_modules()
    return get_bp_instances(bp_modules)


BLUEPRINTS = get_blueprints()
