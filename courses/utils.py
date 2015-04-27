from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError

def get_about_section(course_descriptor, field):
    """
    Faster alternative to courseware.courses.get_course_about_section.
    Returns None if the key does not exist.
    """
    usage_key = course_descriptor.id.make_usage_key("about", field)
    try:
        return modulestore().get_item(usage_key).data
    except ItemNotFoundError:
        return None
