import sys

class RedirectSTDOUTToFile:
    def __init__(self, file):
        self.file = file
