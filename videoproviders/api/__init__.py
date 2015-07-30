from .base import MissingCredentials, ClientError

def get_client(course_key_string):
    """Return the API client most appropriate for this course

    Return:
        client: instance of a BaseClient child class.
    """
    from . import dm
    from . import libcast
    # TODO: define a policy for picking a video provider.
    if False:
        return dm.Client(course_key_string)
    else:
        return libcast.Client(course_key_string)
