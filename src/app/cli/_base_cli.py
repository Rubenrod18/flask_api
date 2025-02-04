from abc import ABC, abstractmethod


class _BaseCli(ABC):
    @abstractmethod
    def run_command(self, *args, **kwargs):
        pass  # pragma: no cover
