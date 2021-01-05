from flask_security import PeeweeUserDatastore

from ..extensions import db_wrapper as db
from app.models.role import Role
from app.models.user import User


UserRoles = User.roles.through_model
user_datastore = PeeweeUserDatastore(db, User, Role, UserRoles)
