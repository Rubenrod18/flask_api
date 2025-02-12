"""Modules for managing data from requests and responses.

Serializers are modules based on Marshmallow.

Marshmallow is an ORM/ODM/framework-agnostic library for converting
complex datatypes, such as objects, to and from native Python datatypes.

In short, marshmallow schemas can be used to:

- Validate input data.
- Deserialize input data to app-level objects.
- Serialize app-level objects to primitive Python types. The serialized
  objects can then be rendered to standard formats such as JSON for use in
  an HTTP API.

References
----------
Pre-/Post-processor Invocation Order:
https://marshmallow.readthedocs.io/en/stable/extending.html?highlight=step1#pre-post-processor-invocation-order  # noqa

"""

from .core import SearchSerializer
from .document import DocumentAttachmentSerializer, DocumentSerializer
from .role import RoleSerializer
from .user import UserExportWordSerializer, UserSerializer
