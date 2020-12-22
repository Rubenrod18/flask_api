from app.managers.base import BaseManager
from app.models.user import User as UserModel


class UserManager(BaseManager):

    def __init__(self):
        super(BaseManager, self).__init__()
        self.model = UserModel
