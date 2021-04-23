import importlib
file = f"/home/runner/work/EclipseDiscordBot/EclipseDiscordBot/constants/version.py"
version = importlib.import_module(file)
print(version.version)
