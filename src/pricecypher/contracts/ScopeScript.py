from abc import ABC, abstractmethod
from typing import Any, Optional

from pricecypher.contracts.Script import Script


class ScopeScript(Script, ABC):
    """
    TODO Comment scope script class
    """

    def execute(self, business_cell_id: Optional[int], bearer_token: str, user_input: dict[Any: Any]) -> Any:
        # Executing a scope-script like a normal script:
        # Attempt to extract the transaction IDs and continue as normal
        transaction_ids: list[int] = user_input['transaction_ids']
        return self.execute_scope_script(business_cell_id, bearer_token, transaction_ids)

    @abstractmethod
    def execute_scope_script(
        self,
        business_cell_id: Optional[int],
        bearer_token: str,
        transaction_ids: list[int]
    ) -> dict[int, str]:
        """
        TODO Comment

        :param business_cell_id:
        :param bearer_token:
        :param transaction_ids:
        :return:
        """
        raise NotImplementedError
