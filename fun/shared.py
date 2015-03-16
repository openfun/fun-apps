import os
import tempfile

from django.conf import settings

"""
Data shared among all LMS/CMS instances of a common environment should be
located in a shared folder designated by settings.SHARED_ROOT. This folder can
be created at runtime in development or test environments, but not in
production. This is a set of utilities for handling paths in this shared
folder.
"""

def ensure_directory_exists(*names):
    """
    Build a path by joining the give names. If the resulting path does not
    exist, create it.

    E.g:

        ensure_directory_exists("submissions", "student_id_1")
    """
    ensure_root_exists()
    path = get_path(*names)
    if not os.path.exists(path):
        os.makedirs(path)

def get_path(*names):
    """
    Return the corresponding path based on the SHARED_ROOT directory.

    E.g:

        get_path("submissions", "student_id_1")
    """
    return os.path.join(root_directory(), *names)

def get_safe_path(*names):
    """
    Return the corresponding path and ensure that the corresponding base directory is created
    """
    path = get_path(*names)
    ensure_directory_exists(os.path.dirname(path))
    return path

def get_course_path(root_dir_in_shared, course, filename):
    """
    Return the full path to a given file for a given course

    E.g:
        get_course_path("answers_distribution_reports", course, "exercise1.csv")
    """

    return get_safe_path(root_dir_in_shared, course.id.to_deprecated_string(), filename)
    
def NamedTemporaryFile(*args, **kwargs):
    """
    Create a temporary file with the same arguments as
    tempfile.NamedTemporaryFile, except that the temporary file will be stored
    in the shared root directory. Directory existence checks will be performed.
    """
    subdirectory = kwargs.get("dir", "")
    ensure_directory_exists(subdirectory)
    kwargs["dir"] = get_path(subdirectory)
    return tempfile.NamedTemporaryFile(*args, **kwargs)

def ensure_root_exists():
    """
    If the directory indicated by the SHARED_ROOT setting does not exist and we
    are not in production, create it. Else, raise an error. You should probably
    not make use of this function directly.
    """
    if not os.path.exists(root_directory()):
        if settings.ENVIRONMENT not in ['test', 'dev']:
            raise ValueError("SHARED_ROOT folder %s does not exist" % root_directory())
        else:
            os.makedirs(settings.SHARED_ROOT)

def root_directory():
    return settings.SHARED_ROOT

