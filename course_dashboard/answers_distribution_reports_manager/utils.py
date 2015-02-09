import os
import unicodedata

from django.conf import settings

from fun import shared

def get_answers_distribution_reports_from_course(course_key):
    """
    Return a list of reports files ordered by date corresponding to a course
    """
    
    course_path = shared.get_path(settings.ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY, course_key.org, course_key.course)

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
