"""Registers database managers.

The managers are classes for managing database queries through
database repositories.

"""

from .base import BaseManager
from .document import DocumentManager
from .role import RoleManager
from .user import UserManager
