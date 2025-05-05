from app.models import User
from app.repositories.base import MySQLRepository


class UserRepository(MySQLRepository):
    def __init__(self):
        super().__init__(model=User)
