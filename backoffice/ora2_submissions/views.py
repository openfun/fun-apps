import os

from django.db import transaction
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from backoffice.utils import get_course, get_course_key, group_required

from . import tasks_api

@group_required('fun_backoffice')
def status(request, course_key_string):
    course = get_course(course_key_string)
    last_file_date = tasks_api.get_last_file_date(course.id)
    task_is_running = tasks_api.is_task_running(course.id)
    return render(request, 'backoffice/ora2_submissions/status.html', {
        'course': course,
        'task_is_running': task_is_running,
        'last_file_date': last_file_date,
    })

@transaction.non_atomic_requests
@require_POST
@group_required('fun_backoffice')
def prepare(request, course_key_string):
    course_key = get_course_key(course_key_string)
    if not tasks_api.is_task_running(course_key):
        tasks_api.submit_preparation_task(request, course_key)
    return redirect('backoffice:ora2-submissions:status',
                    course_key_string=course_key_string)

@group_required('fun_backoffice')
def download(request, course_key_string):
    course_key = get_course_key(course_key_string)
    file_path = tasks_api.get_file_path(course_key)
    if not file_path or not os.path.exists(file_path):
        raise Http404
    response = HttpResponse(open(file_path).read(), content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename="openassessments.tar.gz"'
    return response
