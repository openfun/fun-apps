import hashlib
import hmac
import os
import unicodedata

from django.conf import settings

from fun import shared
from util.file import course_and_time_based_filename_generator

ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY = "answers_distribution_reports"

def get_reports_from_course(course_key):
    """
    Return a list of reports files ordered by date corresponding to a course
    """
    course_path = shared.get_path(ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY, course_key.org, course_key.course)

    if os.path.exists(course_path):
        files = [f for f in os.listdir(course_path) if os.path.isfile(os.path.join(course_path, f))]

        files.sort(key=lambda s: os.path.getmtime(os.path.join(course_path, s)), reverse=True)
        return files
    return None

def remove_accents(input_str):
    """Replace accented caracter by unaccented caracters"""
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii


def build_answers_distribution_report_name(problem):
    """ Build a filename for answer distributions reports.

    The name is based on problem_module display_name and datetime. The report name
    won't exceed 255 bytes.

    Args:
         problem (CapaDescriptor): The problem we get answers distribution from.

    Returns:
        The answer distribution report name (Unicode).
    """
    running_report_name = course_and_time_based_filename_generator(problem.location,
                                                                   problem.display_name)
    running_report_name += u".csv"
    return running_report_name[:255]

def anonymize_username(username):
    """ Anonymize username.
    Args:
        username (unicode)
    Returns:
        (str) A 64-bit hash.
    """
    return hmac.new(settings.ANONYMIZATION_KEY, username, hashlib.sha256).hexdigest()
