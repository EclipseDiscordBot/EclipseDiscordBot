import os
import importlib
file = f"{os.environ['GITHUB_WORKSPACE']}/constants/version.py"
version = importlib.import_module(file)
print(version.version)
