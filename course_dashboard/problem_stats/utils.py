from lxml import etree

from django.core.urlresolvers import reverse

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

def _is_problem(module):
    return True if module.category == 'problem' else False

def build_course_tree(module):
    """ Build a course tree recursively for feeding the jstree in the index page.
    Args:
         module (Descriptor): A module descriptor.
    Returns:
         (Dict, Boolean): (course_tree, is_open)
     """

    children = []
    tree_info = ()
    is_open = False

    for child in module.get_children():
        tree_info = build_course_tree(child)
        children.append(tree_info[0])
        if tree_info[1]:
            is_open = True

    is_problem = _is_problem(module)
    if not module.get_children():
        if is_problem:
            is_open = True

    course_tree = {'text': module.display_name,
                   'children': children,
                   'state': {'opened': is_open},
                   'icon' : 'glyphicon glyphicon-pencil' if is_problem else 'default',
                   'li_attr' : {'category' : 'problem' if is_problem else 'other', 'report_url' :
                                reverse('course-dashboard:reports-manager:generate',
                                        kwargs={'course_id': unicode(module.location.course_key),
                                                'problem_id' : module.location.name}) if is_problem else '#'},
                   'a_attr' : {'href' : reverse('course-dashboard:problem-stats:get-stats',
                                                kwargs={'course_id': unicode(module.location.course_key),
                                                        'problem_id' : module.location.name}) if is_problem else '#'}}

    return (course_tree, is_open)
