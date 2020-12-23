from app.managers.base import BaseManager
from app.models.user import User as UserModel


class UserManager(BaseManager):

    def __init__(self):
        super(BaseManager, self).__init__()
        self.model = UserModel

    def find_by_email(self, email: str):
        return self.model.get_or_none(email=email)
