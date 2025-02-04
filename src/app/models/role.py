import logging

from flask_security import RoleMixin
import sqlalchemy as sa

from .base import Base as BaseModel

logger = logging.getLogger(__name__)

ROLE_NAME_DELIMITER = '_'


class Role(BaseModel, RoleMixin):
    __tablename__ = 'roles'

    name = sa.Column(sa.String(255), nullable=False, unique=True)
    description = sa.Column(sa.Text, nullable=True)
    label = sa.Column(sa.String(255), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(*args, **kwargs)
