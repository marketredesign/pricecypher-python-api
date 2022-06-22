from abc import ABC, abstractmethod
from typing import Any


class Script(ABC):
    config: dict[str, dict[str, Any]] = {}

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def invoke(self, dataset_id: int, **kwargs: dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    def get_config_dependencies(self) -> dict[str, list[str]]:
        raise NotImplementedError

    @abstractmethod
    def get_scope_dependencies(self) -> list[dict[str, Any]]:
        raise NotImplementedError
