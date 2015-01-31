# -*- coding: utf-8 -*-

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from instructor_task.api import get_instructor_task_history
from instructor_task.api_helper import AlreadyRunningError

from backoffice.utils import get_course_key, get_course
from backoffice.views import group_required
from fun_instructor.instructor_task_api import submit_generate_certificate
from utils import (get_running_instructor_tasks,
                  filter_instructor_task,
                  create_test_certificate,
                  get_university_attached_to_course)


@group_required('fun_backoffice')
def certificate_dashboard(request, course_key_string):
    """
    Will display
    . Two panels, pending and previous certificate generation tasks.
    . Two buttons : one two generate a test certificate and the other to trigger a certificate generation task.
    """

    # TODO: only one function that return both the course and the course_key
    course_key = get_course_key(course_key_string)
    course = get_course(course_key_string)

    # generate list of pending background tasks and filter the output
    instructor_tasks = filter_instructor_task(get_running_instructor_tasks(course_key, task_type='certificate-generation'))
    instructor_tasks_history = filter_instructor_task(get_instructor_task_history(course_key, usage_key=None, student=None))

    return render(request, 'backoffice/certificate.html', {
            'course': course,
            'instructor_tasks' : instructor_tasks,
            'instructor_tasks_history' : instructor_tasks_history,
        })

@group_required('fun_backoffice')
def generate_test_certificate(request, course_key_string):
    """
    Return the HttpResponse for downloading the certificate pdf file.
    """

    # TODO: only one function that return both the course and the course_key
    course_key = get_course_key(course_key_string)
    course = get_course(course_key_string)

    university = get_university_attached_to_course(course)
    messages.warning(request, _("University doesn't exist"))
    if university is not None:
        certificate = create_test_certificate(course, course_key, university)
        return certificate_file_response(certificate)
    else:
        return redirect(certificate_dashboard, course_key_string)


def certificate_file_response(certificate):
    """
    Return the HttpResponse for downloading the certificate pdf file.
    """

    response = HttpResponse("", content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(certificate.filename)
    with open(certificate.pdf_file_name, 'r') as gradefile:
        response.write(gradefile.read())
        return response


@group_required('fun_backoffice')
def generate_certificate(request, course_key_string):
    """
    Submit the certificate-generation task to the instructor task api,
    then redirect to the certificate dashboard.
    """

    # TODO: only one function that return both the course and the course_key
    course_key = get_course_key(course_key_string)
    course = get_course(course_key_string)

    # this input dict as to be passed the celery task to operate
    # the instructor_task update api
    # see (get_task_completion_info lms/djangoapps/instructor_task/views.py)
    input_args = {'student' : '',
                  'problem_url' : '',
                  'email_id' : ''}

    if not get_university_attached_to_course(course):
        messages.warning(request, _("University doesn't exist"))
        return redirect(certificate_dashboard, course_key_string)
    try:
        submit_generate_certificate(request, course_key, input_args)
        return redirect(certificate_dashboard, course_key_string)
    except AlreadyRunningError:
        messages.warning(request, _("A certificate generation is already running"))
    return redirect(certificate_dashboard, course_key_string)

