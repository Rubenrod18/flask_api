from app.managers.base import BaseManager
from app.repositories.document import DocumentRepository


class DocumentManager(BaseManager):
    def __init__(self):
        super().__init__(repository=DocumentRepository)
