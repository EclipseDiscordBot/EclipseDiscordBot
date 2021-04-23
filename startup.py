import os
try:
    os.mkdir("data")
    print("created datadir")
except OSError:
    pass
print("Starting startupfile")
os.system("bash -f startupfile.sh")
