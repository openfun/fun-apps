# -*- coding: utf-8 -*-

"""
This file contains all task_class function used by the the instructor_api
"""

from celery import task
from functools import partial

from django.utils.translation import ugettext_noop

from instructor_task.tasks_helper import (
    BaseInstructorTask,
    run_main_task
)

from backoffice.certificate_manager.tasks import generate_certificate
from course_dashboard.reports_manager.tasks import generate_answers_distribution_report
from backoffice.ora2_submissions.tasks import prepare_ora2_submissions


@task(base=BaseInstructorTask)
def generate_certificate_task_class(entry_id, xmodule_instance_args):
    """
    Task class used in submit_generate_certificate.
    """
    
    action_name = ugettext_noop('certified')
    task_fn = partial(generate_certificate, xmodule_instance_args)
    return run_main_task(entry_id, task_fn, action_name)

@task(base=BaseInstructorTask)
def prepare_ora2_submissions_task(entry_id, _xmodule_instance_args):
    action_name = "generated"
    return run_main_task(entry_id, prepare_ora2_submissions, action_name)

@task(base=BaseInstructorTask)
def answers_distribution_report_generation_task_class(entry_id, _xmodule_instance_args):
    action_name = "answers_distribution_report"
    return run_main_task(entry_id, generate_answers_distribution_report, action_name)
