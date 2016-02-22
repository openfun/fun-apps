# -*- coding: utf-8 -*-

from celery.states import READY_STATES
import json
import os
import random


from django.conf import settings

from capa.xqueue_interface import make_hashkey
from instructor_task.models import InstructorTask
from xmodule.modulestore.django import modulestore

from certificates.models import GeneratedCertificate
from courses.models import Course
from fun_certificates.generator import CertificateInfo
from student.models import UserProfile
from teachers.models import CertificateTeacher
from universities.models import University



def get_certificate_params(course_key):
    """Returns required information to pass to CertificateInfo
    to create certificate.

    Args:
        course_key: course if org/number/session

    returns:
        course: modulestore course
        course_display_name: course name
        university: University model
        organization_logo: path of the university logo
        teachers: queryset of certificate teachers
        certificate_language: language
    """

    course = modulestore().get_course(course_key, depth=2)
    course_display_name = unicode(course.display_name).encode('utf-8')
    try:
        university = University.objects.get(code=course.location.org)
    except University.DoesNotExist:
        university = None
    if university and university.certificate_logo:
        logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
    else:
        logo_path = None
    certificate_base_filename = "attestation_suivi_" + (course.id.to_deprecated_string().replace('/', '_')) + '_'

    teachers = get_teachers_list_from_course(course_key)
    certificate_language = Course.get_course_language(unicode(course_key))

    return (course, course_display_name, university, logo_path,
            certificate_base_filename, teachers, certificate_language)


def generate_fun_certificate(student,
                             course_id,
                             course_display_name, course,
                             teachers,
                             organization_display_name, organization_logo,
                             certificate_base_filename, ignore_grades, new_grade, fail_flag):
    """Generates a certificate for one student and one course."""

    profile = UserProfile.objects.get(user=student)
    student_name = unicode(profile.name).encode('utf-8')
    # grade the student
    cert, _created = GeneratedCertificate.objects.get_or_create(
        user=student, course_id=course_id
    )
    request.user = student
    grade = grades.grade(student, request, course)
    cert.grade = grade['percent']
    cert.user = student
    cert.course_id = course_id
    cert.name = profile.name
    fail = False

    if ignore_grades:
        cert.grade = 1
    elif new_grade:
        fail = fail_flag
        cert.grade = new_grade
    elif grade['grade'] is None:
        ## edx grading
        fail = True

    if fail:
        cert.status = status.notpassing
    else:
        key = make_hashkey(random.random())
        cert.key = key
        certificate_filename = certificate_base_filename + key + ".pdf"
        certificate_language = Course.get_course_language(unicode(course_id))
        info = CertificateInfo(
            student_name, course_display_name,
            organization_display_name, organization_logo,
            certificate_filename, teachers, language=certificate_language
        )
        info.generate()

        cert.status = status.downloadable
        cert.download_url = settings.CERTIFICATE_BASE_URL + certificate_filename
    cert.save()
    return cert.status


def create_test_certificate(course, course_key, university):
    """
    Generate the pdf certicate, save it on disk
    """

    (course, course_display_name, university, logo_path,
            certificate_base_filename, teachers,
            certificate_language) = get_certificate_params(course_key)

    key = make_hashkey(random.random())
    filename = "TEST_attestation_suivi_%s_%s.pdf" % (
        course.id.to_deprecated_string().replace('/', '_'), key
    )

    certificate = CertificateInfo(settings.STUDENT_NAME_FOR_TEST_CERTIFICATE,
                                  course_display_name, university.name, logo_path, filename, teachers,
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
    return fun_course.get_first_university()
