from courseware.courses import get_courses, sort_by_announcement
from universities.models import University


def get_university_courses(user, university_code):
    """
    Returns an array containing courses object for the given
    organization.
    """
    courses = get_courses(user)
    if university_code == "other":
        # "other" courses that are associated to organizations that are not
        # listed in the university page.
        university_codes = University.objects.values_list('code', flat=True)
        courses = [c for c in courses if c.org not in university_codes]
    else:
        courses = [c for c in courses if c.org == university_code]
    courses = sort_by_announcement(courses)
    return courses
