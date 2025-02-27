import logging

import sqlalchemy as sa
from flask_security import RoleMixin

from .base import Base

logger = logging.getLogger(__name__)

ROLE_NAME_DELIMITER = '_'

ADMIN_ROLE = 'admin'
TEAM_LEADER_ROLE = 'team_leader'
WORKER_ROLE = 'worker'

ROLES = {ADMIN_ROLE, TEAM_LEADER_ROLE, WORKER_ROLE}


class Role(Base, RoleMixin):
    __tablename__ = 'roles'

    name = sa.Column(sa.String(255), nullable=False, unique=True)
    description = sa.Column(sa.Text, nullable=True)
    label = sa.Column(sa.String(255), nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
