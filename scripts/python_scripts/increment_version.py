import os
import importlib
file = f"{os.environ['GITHUB_WORKSPACE']}.constants.version"
version = importlib.import_module(file)
print(version.version)
