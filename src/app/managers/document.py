from app.managers.base import BaseManager
from app.models.document import Document


class DocumentManager(BaseManager):
    def __init__(self):
        super(DocumentManager, self).__init__()
        self.model = Document
