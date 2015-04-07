# -*- coding: utf-8 -*-

"""
This file contains all submit function use to send a task to the instructor_task api
"""

from instructor_task.api_helper import submit_task

from fun_instructor.tasks import generate_certificate_task_class
from fun_instructor.tasks import answers_distribution_report_generation_task_class


def submit_generate_certificate(request, course_key, query_features):
    """ Request to generate certificate as a background task. """

    task_type = 'certificate-generation'
    task_class = generate_certificate_task_class
    task_input = query_features
    task_key = ""

    return submit_task(request, task_type, task_class, course_key, task_input, task_key)


def submit_generate_answers_distribution_report(request, course_key, task_input):
    """ Request to generate certificate as a background task. """

    task_type = 'answers-distribution-report-generation'
    task_class = answers_distribution_report_generation_task_class
    task_input = task_input
    return submit_task(request, task_type, task_class, course_key, task_input, "")




