from lxml import etree
from capa import responsetypes

def fetch_problems(store, course_key):
    """Fetches all problem corresponding to a course from the module store.

    Args:
         store (ModuleStore): The module store to search from.
         course_location (BlockUsageLocator): The course location.

    Return:
         list: A list of problems (CapaDescriptor).
     """
    qualifiers = {'qualifiers' : {'category' : 'problem'}}
    return store.get_items(course_key, **qualifiers)

def fetch_problem(store, course_key, problem_id):
    """Fetches a problem corresponding to a course from the module store.

    Args:
         store (ModuleStore): The module store to search from.
         course_key (SlashSeparatedCourseKey): The course key.
         problem_id (str): The problem id as string.

    Returns:
         CapaDescriptor: The corresponding problem.
     """
    usage_key = course_key.make_usage_key('problem', problem_id)
    return store.get_item(usage_key)

def fetch_ancestors_names(store, item_location):
    """Fetches module's ancestors names.

    Args:
        store (ModuleStore): The module store to search from.
        item_location (BlockUsageLocator): The item location.

    Returns:
        list: An list of ancestors modules names begining by the farthest.
     """
    parent_item = store.get_parent_location(item_location)
    if not parent_item:
        return []
    ancestors_names = fetch_ancestors_names(store, parent_item)
    ancestors_names.append(store.get_item(parent_item).display_name)
    return ancestors_names

def get_problem_size(problem):
    """Get the problem number of questions.
    Args:
         problem (CapaDescriptor)

    Returns:
         Int: The number of questions.
     """

    tree = etree.XML(problem.data)
    registered_tags = responsetypes.registry.registered_tags()
    questions = [node.tag for node in tree.iter() if node.tag in registered_tags]
    return len(questions)

def percentage(part, whole):
    return round(100 * float(part)/float(whole), 2)
