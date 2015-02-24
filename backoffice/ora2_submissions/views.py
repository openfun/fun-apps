import os

from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from backoffice.utils import get_course, get_course_key, group_required

from . import tasks

@group_required('fun_backoffice')
def status(request, course_key_string):
    course = get_course(course_key_string)
    last_file_date = tasks.get_last_file_date(course.id)
    is_task_running = tasks.is_task_running(course.id)
    return render(request, 'backoffice/ora2_submissions/status.html', {
        'course': course,
        'is_task_running': is_task_running,
        'last_file_date': last_file_date,
    })

@require_POST
@group_required('fun_backoffice')
def prepare(request, course_key_string):
    course_key = get_course_key(course_key_string)
    if not tasks.is_task_running(course_key):
        tasks.submit_preparation_task(request, course_key)
    return redirect('backoffice:ora2-submissions:status',
                    course_key_string=course_key_string)

@group_required('fun_backoffice')
def download(request, course_key_string):
    course_key = get_course_key(course_key_string)
    file_path = tasks.get_file_path(course_key)
    if not file_path or not os.path.exists(file_path):
        raise Http404
    response = HttpResponse(open(file_path).read(), content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename="openassessments.tar.gz"'
    return response
