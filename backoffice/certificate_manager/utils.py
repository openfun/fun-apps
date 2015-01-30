# -*- coding: utf-8 -*-

import json
import os
import random

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from capa.xqueue_interface import make_hashkey

from backoffice.models import Teacher
from fun_certificates.generator import CertificateInfo
from universities.models import University


def create_test_certificate(course, course_key, university):
    """
    Generate the pdf certicate, save it on disk
    """

    if university.certificate_logo:
        logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
    else:
        logo_path = None

    teachers = get_teachers_list_from_course(course_key)

    key = make_hashkey(random.random())
    filename = "TEST_attestation_suivi_%s_%s.pdf" % (
        course.id.to_deprecated_string().replace('/', '_'), key
    )

    certificate = CertificateInfo(settings.STUDENT_NAME_FOR_TEST_CERTIFICATE,
        course.display_name, university.name, logo_path, filename, teachers
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
            instructor_task.task_output = {'total' : 0,
                                           'downloadable' : 0,
                                           'notpassing': 0 }
    return instructor_tasks


def get_teachers_list_from_course(course_key):
    """
    Return the teachers/title list attached to course
    """

    teachers = Teacher.objects.filter(course__key=str(course_key))
    teachers_list = [u"{}/{}".format(teacher.full_name, teacher.title) for teacher in teachers]
    return teachers_list



def get_university_attached_to_course(course):
    """
    Get the university attached to a course return 'None' if not found
    """
    try:
        university = University.objects.get(code=course.org)
    except University.DoesNotExist:
        university = None
    return university


