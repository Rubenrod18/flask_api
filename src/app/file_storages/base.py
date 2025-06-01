from abc import ABC, abstractmethod


class BaseFileStorage(ABC):
    """Abstract interface for file storage operations."""

    @abstractmethod
    def save_bytes(self, file_content: bytes, filename: str, override: bool = False):
        raise NotImplementedError

    @abstractmethod
    def copy_file(self, src: str, dst: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_filesize(self, filepath: str) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_basename(self, filename: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def rename(self, src: str, dst: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, filepath: str) -> None:
        raise NotImplementedError
