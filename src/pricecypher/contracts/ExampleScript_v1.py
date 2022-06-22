from typing import Any

from pricecypher.contracts.ScopeScript import ScopeScript
from pricecypher.contracts.Script import Script


class ExampleScopeScript(ScopeScript):
    def invoke_scope_script(self, dataset_id: int, transaction_ids: list[int]) -> dict[int, str]:
        print('ok')
        print(dataset_id)
        print(transaction_ids)

        if self.config['script_sec']['base_on'] == 'margin':
            return {
                transaction_ids[0]: str(2 * self.config['script_sec']['margin_scale']),
            }
        else:
            return {
                transaction_ids[0]: str(3),
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
    import pickle
    with open("test_script.pkl", "wb") as dill_file:
        pickle.dump(ExampleScopeScript, dill_file)

    with open("test_script.pkl", "rb") as script_file:
        theClass = pickle.load(script_file)

    config = {
        'script_sec': {
            'base_on': 'margin',
            'margin_scale': 4,
        },
    }
    inp = {
        'somefield': 8,
        'transaction_ids': [5, 6, 8],
    }
    inst: Script = theClass(config)
    reqConfig = inst.get_config_dependencies()
    reqScopes = inst.get_scope_dependencies()
    output = inst.invoke(2, **inp)
    print(reqConfig)
    print(reqScopes)
    print(output)




