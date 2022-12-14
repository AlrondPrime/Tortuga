import importlib.util
import os
import sys


def checkPackages(modules: list):
    for name in modules:
        if name in sys.modules:
            print(f"{name!r} already in sys.modules")
        elif (spec := importlib.util.find_spec(name)) is not None:
            # If you choose to perform the actual import ...
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            print(f"{name!r} has been imported")
        else:
            os.system("pip install psutil")
            exit(0)
        # else:
        #     print(f"can't find the {name!r} module")
        #     exit(-1)
