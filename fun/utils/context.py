import os

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)
        self.saved_path = None

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)

class setenv:
    """Context manager for changing environment variables"""
    def __init__(self, name, new_value):
        self.name = name
        self.new_value = new_value
        self.saved_value = None

    def __enter__(self):
        self.saved_value = os.environ.get(self.name)
        self.set(self.new_value)
        return self

    def __exit__(self, etype, value, traceback):
        self.set(self.saved_value)

    def set(self, value):
        if value is None:
            if self.name in os.environ:
                del os.environ[self.name]
        else:
            os.environ[self.name] = value
