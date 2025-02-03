import logging

from flask_security import RoleMixin
import sqlalchemy as sa
from sqlalchemy.orm import mapped_column

from .base import Base as BaseModel

logger = logging.getLogger(__name__)


class Role(BaseModel, RoleMixin):
    __tablename__ = 'roles'

    name = mapped_column(sa.String(255), nullable=False, use_existing_column=True)
    description = sa.Column(sa.Text, nullable=True)
    label = sa.Column(sa.String(255), nullable=False)

    def __init__(self, *args, **kwargs):
        super(Role, self).__init__(*args, **kwargs)
