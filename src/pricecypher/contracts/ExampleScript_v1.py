from typing import Any, Optional

import numpy as np

from pricecypher.contracts import Script, ScopeScript


class ExampleScopeScript(ScopeScript):
    def execute_scope_script(
        self,
        business_cell_id: Optional[int],
        bearer_token: str,
        transaction_ids: list[int]
    ) -> dict[int, str]:
        arr = np.array([5, 7, 9])

        if self.config['script_sec']['base_on'] == 'margin':
            return {
                transaction_ids[0]: str(2 * self.config['script_sec']['margin_scale'] * arr[0]),
            }
        else:
            return {
                transaction_ids[0]: str(3 + arr[2]),
            }

    def get_config_dependencies(self) -> dict[str, list[str]]:
        if 'script_sec' not in self.config:
            return {'script_sec': []}
        elif 'base_on' not in self.config['script_sec']:
            return {'script_sec': ['base_on']}
        elif self.config['script_sec']['base_on'] == 'margin' and 'margin_scale' not in self.config['script_sec']:
            return {'script_sec': ['margin_scale']}
        else:
            return {}

    def get_scope_dependencies(self) -> list[dict[str, Any]]:
        return [{'representation': 'gross_price'}, {'representation': 'bm'}]


if __name__ == '__main__':
    dataset_id = 10
    business_cell_id = None
    bearer_token = "Bearer some_token"
    settings = {}
    config = {
        'script_sec': {
            'base_on': 'margin',
            'margin_scale': 4,
        },
    }
    transactions = [5, 6, 8]
    inst: ScopeScript = ExampleScopeScript(dataset_id, settings, config)
    reqConfig = inst.get_config_dependencies()
    reqScopes = inst.get_scope_dependencies()
    output = inst.execute_scope_script(business_cell_id, bearer_token, transactions)
    print(reqConfig)
    print(reqScopes)
    print(output)
