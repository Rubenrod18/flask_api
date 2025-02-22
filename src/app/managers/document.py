from app.managers.base import BaseManager
from app.models.document import Document


class DocumentManager(BaseManager):
    def __init__(self):
        super().__init__(model=Document)
