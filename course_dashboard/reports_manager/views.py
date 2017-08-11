# -*- coding: utf-8 -*-

import os

from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, Http404

from instructor_task.api_helper import AlreadyRunningError
from xmodule.modulestore.django import modulestore

from backoffice.utils import get_course_key
from backoffice.certificate_manager.utils import get_running_instructor_tasks
from fun_instructor.instructor_task_api.submit_tasks import submit_generate_answers_distribution_report
from util.views import ensure_valid_course_key
from fun.utils.views import staff_required_or_level
from fun import shared
from course_dashboard.reports_manager.utils import fetch_problem

from course_dashboard.reports_manager.utils import (build_answers_distribution_report_name,
                                                    get_reports_from_course,
                                                    remove_accents,
                                                    ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY)

@ensure_valid_course_key
@staff_required_or_level('staff')
def dashboard(request, course_id):
    """
    Will display two panels : the first one lists current processing reports,
    and the other lists all answer distribution reports corresponding to the course
    """
    course_key = get_course_key(course_id)
    answers_distribution_reports = get_reports_from_course(course_key)
    running_reports_generation = get_running_instructor_tasks(
        course_key,
        ['answers-distribution-report-generation']
    )
    return render(request, 'course_dashboard/reports_manager/dashboard.html',
                  {"course_id": course_id,
                   "active_tab": "reports",
                   "answers_distribution_reports": answers_distribution_reports,
                   "running_reports_generation": running_reports_generation})

@transaction.non_atomic_requests
@ensure_valid_course_key
@staff_required_or_level('staff')
def generate(request, course_id, problem_id):
    """ Submit 'generate_answers_distribution_report' task to celery.

    Args:
         course_id (str): The course id as string.
         problem_id (str): The problem id as string.

    Return:
         Redirect to Report Manager dashboard.
    """
    store = modulestore()
    course_key = get_course_key(course_id)
    problem = fetch_problem(store, course_key, problem_id)

    running_report_name = build_answers_distribution_report_name(problem)

    input_args = {'problem_id': problem_id,
                  'running_report_name': running_report_name}

    try:
        submit_generate_answers_distribution_report(request, course_key, input_args)
        return redirect('course-dashboard:reports-manager:dashboard', course_id)
    except AlreadyRunningError:
        messages.warning(request, _("A report on answers distribution is already running"))
        return redirect('course-dashboard:reports-manager:dashboard', course_id)

@ensure_valid_course_key
@staff_required_or_level('staff')
def download(request, course_id, answers_distribution_report):
    course_key = get_course_key(course_id)

    file_path = shared.get_path(ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY,
                                course_key.org, course_key.course,
                                answers_distribution_report)

    if not file_path or not os.path.exists(file_path):
        raise Http404

    response = HttpResponse(open(file_path).read(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(remove_accents(answers_distribution_report))
    return response
