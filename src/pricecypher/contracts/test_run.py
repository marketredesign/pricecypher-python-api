import abc
import inspect
import sys

from pricecypher.contracts import ScopeScript, Script

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
        if callable(attr) and type(attr) == abc.ABCMeta:
            print(attr, type(attr))
            # TODO Check extends script but is not abstract (does not directly extend ABC)
            return attr

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
    inst: Script = clazz(config)
    reqConfig = inst.get_config_dependencies()
    reqScopes = inst.get_scope_dependencies()
    output = inst.invoke(2, **inp)
    print(reqConfig)
    print(reqScopes)
    print(output)
