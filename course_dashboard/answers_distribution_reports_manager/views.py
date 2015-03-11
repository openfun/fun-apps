# -*- coding: utf-8 -*-

import os

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, Http404

from instructor_task.api_helper import AlreadyRunningError
from xmodule.modulestore.django import modulestore

from backoffice.utils import get_course_key, get_course
from backoffice.certificate_manager.utils import get_running_instructor_tasks
from course_dashboard.answers_distribution import get_problem_module, add_ancestors_names_to_problem_module
from fun_instructor.instructor_task_api.submit_tasks import submit_generate_answers_distribution_report
from fun.utils.views import ensure_valid_course_key
from fun.utils.views import staff_required_or_level
from fun import shared

from utils import get_answers_distribution_reports_from_course, remove_accents

@ensure_valid_course_key
@staff_required_or_level('staff')
def dashboard(request, course_id):
    """
    Will display two panels : the first one lists current processing reports,
    and the other lists all answer distribution reports corresponding to the course
    """
    
    course_key = get_course_key(course_id)
    
    answers_distribution_reports = get_answers_distribution_reports_from_course(course_key)
    running_reports_generation = get_running_instructor_tasks(course_key, 'answers-distribution-report-generation')
    return render(request, 'course_dashboard/answers_distribution_reports_manager/dashboard.html',
                  {"course_id": course_id,
                   "answers_distribution_reports" : answers_distribution_reports,
                   "running_reports_generation" : running_reports_generation})

@ensure_valid_course_key
@staff_required_or_level('staff')
def generate(request, course_id, problem_module_id):
    """
    launch the generate_answers_distribution_report task and redirect to  dashboard
    """

    course_key = get_course_key(course_id)

    ## Get the name of the problem module and of its ancestors
    store = modulestore()    
    problem_module = get_problem_module(course_id, problem_module_id)
    add_ancestors_names_to_problem_module(problem_module[0], store)
    running_report_name = u"{}-{}-{}/{}.csv".format(
                                              course_key.org,
                                              course_key.course,
                                              problem_module[0].ancestors_names['great_grandparent'][:100],
                                              problem_module[0].display_name[:100])
              
    input_args = {'problem_module_id' : problem_module_id, 'running_report_name' : running_report_name}
    
    try:
        submit_generate_answers_distribution_report(request, course_key, input_args)
        return redirect('course-dashboard:answers-distribution-reports-manager:dashboard', course_id)
    except AlreadyRunningError:
        messages.warning(request, _("A report on answers distribution is already running"))
        return redirect('course-dashboard:answers-distribution', course_id)

@ensure_valid_course_key
@staff_required_or_level('staff')
def download(request, course_id, answers_distribution_report):
    
    course_key = get_course_key(course_id)
    
    file_path = shared.get_path(settings.ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY,
                                course_key.org, course_key.course,
                                answers_distribution_report)

    if not file_path or not os.path.exists(file_path):
        raise Http404
    
    response = HttpResponse(open(file_path).read(), content_type='text/csv')
    
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(remove_accents(answers_distribution_report))

    return response
