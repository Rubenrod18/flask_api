from app.models.document import Document
from app.repositories.base import MySQLRepository


class DocumentRepository(MySQLRepository):
    def __init__(self):
        super().__init__(model=Document)
