"""Registers database repositories.

They are responsible for encapsulating the logic of querying, creating,
updating, or deleting records in the database, abstracting the interaction
with the ORM.

"""

from .document import DocumentRepository
from .role import RoleRepository
from .user import UserRepository
