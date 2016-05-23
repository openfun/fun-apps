# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from instructor_task.api import get_instructor_task_history
from instructor_task.api_helper import AlreadyRunningError

from backoffice.utils import get_course_key, get_course

from ..utils import group_required
from .utils import (
    create_test_certificate,
    filter_instructor_task,
    get_running_instructor_tasks,
    get_university_attached_to_course,
)
from fun_instructor.instructor_task_api.submit_tasks import (
    submit_generate_certificate, submit_generate_verified_certificate
)


@group_required('fun_backoffice')
def certificate_dashboard(request, course_key_string):
    """Certificate management dashboard for the support team."""

    course_key = get_course_key(course_key_string)
    course = get_course(course_key_string)
    if course is None:
        raise Http404

    # generate list of pending background tasks and filter the output
    task_types = ['certificate-generation', 'verified-certificate-generation']
    instructor_tasks = filter_instructor_task(
        get_running_instructor_tasks(course_key, task_types)
    )

    # Get list of tasks sorted by decreasing id
    instructor_tasks_history = []
    for task_type in task_types:
        instructor_tasks_history += list(filter_instructor_task(
           get_instructor_task_history(course_key, task_type=task_type, usage_key=None, student=None)
        ))
    instructor_tasks_history.sort(key=lambda x: -x.id)

    return render(request, 'backoffice/certificate.html', {
        'course': course,
        'certificate_base_url' : settings.CERTIFICATE_BASE_URL,
        'instructor_tasks' : instructor_tasks,
        'instructor_tasks_history' : instructor_tasks_history,
    })

@group_required('fun_backoffice')
def generate_test_certificate(request, course_key_string):
    """
    Return the HttpResponse for downloading the certificate pdf file.
    """
    course_key = get_course_key(course_key_string)
    university = get_university_attached_to_course(course_key)
    if university is not None:
        certificate = create_test_certificate(course_key)
        return certificate_file_response(certificate)
    else:
        messages.warning(request, _("University doesn't exist"))
        return redirect('backoffice:certificate-dashboard', course_key_string)


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
def generate_certificate(request, course_key_string, verified=False):
    """
    Submit the certificate-generation task to the instructor task api,
    then redirect to the certificate dashboard.
    """
    course_key = get_course_key(course_key_string)

    if not get_university_attached_to_course(course_key):
        messages.warning(request, _("University doesn't exist"))
        return redirect('backoffice:certificate-dashboard', course_key_string)
    try:
        if verified:
            submit_generate_verified_certificate(request, course_key)
        else:
            submit_generate_certificate(request, course_key)
        return redirect('backoffice:certificate-dashboard', course_key_string)
    except AlreadyRunningError:
        messages.warning(request, _("A certificate generation is already running"))
    return redirect('backoffice:certificate-dashboard', course_key_string)
