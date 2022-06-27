from typing import Any, Optional

import numpy as np

from pricecypher.contracts import ScopeScript


class ExampleScopeScript(ScopeScript):
    def execute_scope_script(
        self,
        business_cell_id: Optional[int],
        bearer_token: str,
        transaction_ids: list[int]
    ) -> dict[int, str]:
        # Example of using a package
        np_arr = np.array(transaction_ids)

        if self.config['script_sec']['base_on'] == 'margin':
            return {
                int(id): str(id + 2 * self.config['script_sec']['margin_scale']) for id in np_arr
            }
        else:
            return {
                int(id): str(id + 3) for id in np_arr
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
