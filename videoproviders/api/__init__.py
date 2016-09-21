import importlib

from .base import MissingCredentials, ClientError


VIDEO_CLIENT_MODULE = "videoproviders.api.videofront"
VIDEO_CLIENT_CLASS = "Client"


def get_client(course_key_string):
    """Return the API client most appropriate for this course

    Return:
        client: instance of a BaseClient child class.
    """
    module = importlib.import_module(VIDEO_CLIENT_MODULE)
    return getattr(module, VIDEO_CLIENT_CLASS)(course_key_string)
