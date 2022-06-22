import abc
import inspect
import sys
from typing import Collection

from pricecypher.contracts import ScopeScript
from pricecypher.contracts.Script import Script

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


def oldPickle():
    import pickle
    with open("test_script.pkl", "rb") as script_file:
        theClass = pickle.load(script_file)

    inst: Script = theClass(config)
    reqConfig = inst.get_config_dependencies()
    reqScopes = inst.get_scope_dependencies()
    output = inst.invoke(2, **inp)
    print(reqConfig)
    print(reqScopes)
    print(output)


def extract_class(file: str):
    assert file.endswith('.py')
    modul = __import__(file[:-3])
    for attr_name in dir(modul):
        attr = getattr(modul, attr_name)
        # Check attribute is callable, it is a class, it extends Script, and is not an abstract class itself
        if callable(attr) and type(attr) == abc.ABCMeta and \
                Script in extract_parents_deep(attr) and abc.ABC not in attr.__bases__:
            return attr


def extract_parents_deep(clazz: type) -> Collection[type]:
    bases: set[type] = set(clazz.__bases__)
    if len(bases) == 0:
        return bases
    else:
        for base in bases:
            bases = bases.union(extract_parents_deep(base))
        return bases


if __name__ == '__main__':
    print(type(Script))
    run = 'ExampleScript_v1.py'
    modul = __import__(run[:-3])
    print(modul)
    # inst = modul([])
    # print(inst)

    print('==extracting')
    clazz = extract_class(run)
    print('===')
    print(clazz)
    print(clazz.__bases__)
    print(extract_parents_deep(clazz))
    print(Script)
    print(abc.ABC)
    print('====')
    inst: Script = clazz(config)
    reqConfig = inst.get_config_dependencies()
    reqScopes = inst.get_scope_dependencies()
    output = inst.invoke(2, **inp)
    print(reqConfig)
    print(reqScopes)
    print(output)
