import json
import time

from django.http import HttpResponse, Http404
from django.shortcuts import render

from eventtracking import tracker
from opaque_keys.edx.keys import CourseKey
from util.views import ensure_valid_course_key
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError

from course_dashboard.problem_stats import utils
from course_dashboard.problem_stats.problem_monitor import ProblemMonitor
from fun.utils.views import staff_required_or_level

@ensure_valid_course_key
@staff_required_or_level('staff')
def index(request, course_id):
    """ Render the course tree with all course problems (LoncapaProblem).

    Args:
         course_id (str): The course id as string.
    """
    start_time = time.time()

    # Does the course exist?
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)
    if course is None:
        raise Http404()

    course_tree = utils.build_course_tree(course)

    tracker.emit("course_dashboard.problem_stats.views.index",
                 {'task-time' : time.time() - start_time})

    return render(request, 'problem_stats/index.html', {
        "course_id": course_id,
        "course_tree_data" : json.dumps(course_tree)
    })

@ensure_valid_course_key
@staff_required_or_level('staff')
def get_stats(request, course_id, problem_id):
    """ et stats for a single problem (LoncapaProblem).

    The problem id is passed has a GET paramater with 'problem_id' key.

    Args:
         course_id (str): The course id as string.
     """
    start_time = time.time()
    store = modulestore()
    course_key = CourseKey.from_string(course_id)

    try:
        problem = utils.fetch_problem(store, course_key, problem_id)
    except ItemNotFoundError:
        raise Http404()
    problem_monitor = ProblemMonitor(problem)
    problem_monitor.get_student_answers()
    tracker.emit("course_dashboard.problem_stats.views.get_stats",
                 {'task-time' : time.time() - start_time})

    return HttpResponse(problem_monitor.get_html())
