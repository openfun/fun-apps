from universities.models import University


def get_university_by_code(code):
    """
    Returns the university object for the given code.
    """
    try:
        university = University.objects.get(code=code)
    except University.DoesNotExist:
        university = None
    return university
