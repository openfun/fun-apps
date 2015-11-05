from .base import MissingCredentials, ClientError

def get_client(course_key_string):
    """Return the API client most appropriate for this course

    Return:
        client: instance of a BaseClient child class.
    """
    if True:
        from . import libcast
        return libcast.Client(course_key_string)
