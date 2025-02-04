from app.extensions import db
from app.managers.base import BaseManager
from app.models.user import User as UserModel


class UserManager(BaseManager):

    def __init__(self):
        super(BaseManager, self).__init__()
        self.model = UserModel

    def find_by_email(self, email: str, *args):
        query = (self.model.email == email,)
        if args:
            query = query + args
        return db.session.query(self.model).filter(*query).first()

    def get_last_record(self):
        return db.session.query(self.model).order_by(self.model.id.desc()).limit(1).first()
