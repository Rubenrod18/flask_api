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
        return self.model.get_or_none(*query)

    def get_last_record(self):
        return (self.model.select()
                .order_by(UserModel.id.desc())
                .limit(1)
                .first())
