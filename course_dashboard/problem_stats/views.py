from django.http import HttpResponse, Http404
from django.shortcuts import render

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from fun.utils.views import ensure_valid_course_key
from fun.utils.views import staff_required_or_level

from course_dashboard.problem_stats import utils
from course_dashboard.problem_stats.problem_monitor import ProblemMonitor

@ensure_valid_course_key
@staff_required_or_level('staff')
def index(request, course_id):
    """ List all course problems (LoncapaProblem) and render them in the course_dashboard.

    Render the index.html template with the course_id and problems(list of CapaDescriptor) as context.

    Args:
         course_id (str): The course id as string.
    """
    course_key = CourseKey.from_string(course_id)
    store = modulestore()

    problems = utils.fetch_problems(store, course_key)

    for problem in problems:
        ancestors_names = utils.fetch_ancestors_names(store, problem.location)
        if ancestors_names:
            ancestors_names.pop(0)
        problem.ancestors_names = ancestors_names
    return render(request, 'problem_stats/index.html', {
        "course_id": course_id,
        "problems" : problems
    })

@ensure_valid_course_key
@staff_required_or_level('staff')
def get_stats(request, course_id):
    """ et stats for a single problem (LoncapaProblem).

    The problem id is passed has a GET paramater with 'problem_id' key.

    Args:
         course_id (str): The course id as string.
     """

    course_key = CourseKey.from_string(course_id)
    store = modulestore()

    if not 'problem_id' in request.GET:
        return Http404

    problem = utils.fetch_problem(store, course_key, request.GET['problem_id'])
    problem_monitor = ProblemMonitor(problem)
    problem_monitor.get_student_answers()

    return HttpResponse(problem_monitor.get_html())
