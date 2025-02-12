from app.managers.base import BaseManager
from app.models.document import Document as DocumentModel


class DocumentManager(BaseManager):
    def __init__(self):
        super(DocumentManager, self).__init__()
        self.model = DocumentModel
