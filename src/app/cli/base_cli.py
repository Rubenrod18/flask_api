from abc import ABC, abstractmethod


class BaseCli(ABC):
    @abstractmethod
    def run_command(self, *args, **kwargs):
        raise NotImplementedError
