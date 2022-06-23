from abc import ABC, abstractmethod
from typing import Any, Optional, Annotated


class Script(ABC):
    """
    TODO Comment Script class
    """

    dataset_id: Annotated[int, "The dataset ID"] = None  # A comment
    settings: dict[str, Any]
    config: dict[str, dict[str, Any]] = {}

    def __init__(self, dataset_id: int, settings: dict[str, any], config: dict[str, dict[str, Any]]):
        self.dataset_id = dataset_id
        self.settings = settings
        self.config = config

    @abstractmethod
    def get_config_dependencies(self) -> dict[str, list[str]]:
        """
        TODO Comment

        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def get_scope_dependencies(self) -> list[dict[str, Any]]:
        """
        TODO Comment

        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def execute(self, business_cell_id: Optional[int], bearer_token: str, user_input: dict[Any: Any]) -> Any:
        """
        TODO Comment

        :param business_cell_id:
        :param bearer_token:
        :param user_input:
        :return:
        """
        raise NotImplementedError
