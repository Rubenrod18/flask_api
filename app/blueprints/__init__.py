from .base import blueprint as blueprint_base
from .auth import blueprint as blueprint_auth
from .users import blueprint as blueprint_users
from .roles import blueprint as blueprint_roles
from .documents import blueprint as blueprint_documents
from .tasks import blueprint as blueprint_tasks

blueprints = [
    blueprint_base,
    blueprint_users,
    blueprint_roles,
    blueprint_auth,
    blueprint_documents,
    blueprint_tasks,
]