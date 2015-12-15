# -*- coding: utf-8 -*-

from celery.states import READY_STATES
import json
import os
import random


from django.conf import settings

from capa.xqueue_interface import make_hashkey
from instructor_task.models import InstructorTask

from courses.models import Course
from teachers.models import CertificateTeacher
from fun_certificates.generator import CertificateInfo


def create_test_certificate(course, course_key, university):
    """
    Generate the pdf certicate, save it on disk
    """

    if university.certificate_logo:
        logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
    else:
        logo_path = None

    teachers = get_teachers_list_from_course(course_key)
    certificate_language = Course.get_course_language(unicode(course_key))
    key = make_hashkey(random.random())
    filename = "TEST_attestation_suivi_%s_%s.pdf" % (
        course.id.to_deprecated_string().replace('/', '_'), key
    )

    certificate = CertificateInfo(settings.STUDENT_NAME_FOR_TEST_CERTIFICATE,
                                  course.display_name, university.name, logo_path, filename, teachers,
                                  language=certificate_language
    )

    certificate.generate()

    return certificate

def filter_instructor_task(instructor_tasks):
    """
    Parse instructor_task.task_output string to a json dict
    """

    for instructor_task in instructor_tasks:
        if instructor_task.task_output:
            instructor_task.task_output = json.loads(instructor_task.task_output)
        else:
            instructor_task.task_output = {
                'total' : 0,
                'downloadable' : 0,
                'notpassing': 0
            }
    return instructor_tasks

def get_running_instructor_tasks(course_id, task_type):
    """
    Returns a query of InstructorTask objects of running tasks for a given course and task type
    """
    instructor_tasks = InstructorTask.objects.filter(course_id=course_id, task_type=task_type)
    # exclude states that are "ready" (i.e. not "running", e.g. failure, success, revoked):
    for state in READY_STATES:
        instructor_tasks = instructor_tasks.exclude(task_state=state)
    return instructor_tasks.order_by('-id')


def get_teachers_list_from_course(course_key):
    """
    Return the teachers/title list attached to course
    """

    teachers = [certificate_teacher.teacher for certificate_teacher in \
        CertificateTeacher.objects.filter(course__key=str(course_key)).select_related("teacher")]
    teachers_list = [u"{}/{}".format(teacher.full_name, teacher.title) for teacher in teachers]
    return teachers_list


def get_university_attached_to_course(course):
    """
    Get the university attached to a course return 'None' if not found
    """
    fun_course = Course.objects.get(key=unicode(course.id))
    return fun_course.first_university
