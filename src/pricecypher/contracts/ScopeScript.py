from abc import ABC, abstractmethod
from typing import Any

from pricecypher.contracts.Script import Script


class ScopeScript(Script, ABC):

    def invoke(self, dataset_id: int, **kwargs: Any) -> Any:
        transaction_ids: list[int] = kwargs['transaction_ids']
        return self.invoke_scope_script(dataset_id, transaction_ids)

    @abstractmethod
    def invoke_scope_script(self, dataset_id: int, transaction_ids: list[int]) -> dict[int, str]:
        pass

