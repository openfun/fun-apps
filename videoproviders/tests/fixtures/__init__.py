import os

def get_content(file_name):
    """Read the content of the fixtures file stored in the current folder.

    Returns:
        unicode: file content
    """
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read().decode('utf-8')
