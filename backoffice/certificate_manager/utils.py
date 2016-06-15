# -*- coding: utf-8 -*-

import json
import os
import random
import logging

from celery.states import READY_STATES

from django.conf import settings
from django.test.client import RequestFactory  # Importing from tests, I know, I know...

from capa.xqueue_interface import make_hashkey
from certificates.api import emit_certificate_event
from courseware import grades
from instructor_task.models import InstructorTask
from xmodule.modulestore.django import modulestore

from certificates.models import GeneratedCertificate, CertificateStatuses
from courses.models import Course
from fun_certificates.generator import CertificateInfo
from teachers.models import CertificateTeacher
from universities.models import University

from .verified import get_student_certificate_grade

logger = logging.getLogger(__name__)


def get_certificate_params(course_key):
    """Returns required information to pass to CertificateInfo
    to create certificate.

    Args:
        course_key (CourseKey)

    returns:
        course_display_name: course name
        university: University model or None
        teachers: queryset of certificate teachers
        certificate_language: language
    """

    course = modulestore().get_course(course_key, depth=2)
    course_display_name = unicode(course.display_name).encode('utf-8')
    try:
        university = get_university_attached_to_course(course_key)
    except University.DoesNotExist:
        # Note: this is probably a very bad idea, since we are going to use the
        # university.name attribute in the rest of the certificate generation.
        university = None

    teachers = get_teachers_list_from_course(course_key)
    certificate_language = Course.get_course_language(unicode(course_key))

    return (course_display_name, university, teachers, certificate_language)


def generate_fun_certificate(student, course, teachers, university):
    """Generates a certificate for one student and one course."""

    # grade the student
    cert, _created = GeneratedCertificate.objects.get_or_create(
        user=student, course_id=course.id
    )

    # TODO We need to create a request object manually. It's very ugly and we should
    # do something about it.
    request = RequestFactory().get('/')
    request.session = {}
    request.user = student

    grade = grades.grade(student, request, course)
    cert.grade = grade['percent']
    cert.name = student.profile.name

    if grade['grade'] is None:
        cert.status = CertificateStatuses.notpassing
    else:
        key = make_certificate_hash_key()
        certificate_filename = "attestation_suivi_{}_{}.pdf".format(
            (unicode(course.id).replace('/', '_')),
            key
        )
        cert.key = key
        certificate_language = Course.get_course_language(unicode(course.id))
        course_display_name = unicode(course.display_name).encode('utf-8')

        CertificateInfo(
            student.profile.name, course_display_name,
            university,
            certificate_filename, teachers, language=certificate_language
        ).generate()

        set_certificate_filename(cert, certificate_filename)
    cert.save()
    logger.info("Honor certificate status for student {}: {}".format(student.username, cert.status))

    trigger_tracking_log(cert, course, student)

    return cert.status


def trigger_tracking_log(cert, course, student):
    """
    Log the certificate generation for a certificate, a course and a student in
    EDX tracking logs (same process as in EDX).
    """
    if cert.status in [CertificateStatuses.generating, CertificateStatuses.downloadable]:
        emit_certificate_event('created', student, course.id, course, {
            'user_id': student.id,
            'course_id': unicode(course.id),
            'certificate_id': cert.verify_uuid,
            'enrollment_mode': cert.mode,
        })


def generate_fun_verified_certificate(student, course, force_grade=False):
    """Generates a verified certificate.,
    if the student's grade is greater or equal to course's passing grade.

    We can force the creation of a certificate with the optionnal parameter grade
    (can be useful in specific users certificate generation (ie : backoffice or management command)
    """

    grade = force_grade or get_student_certificate_grade(course.id, student)
    logger.info("trying to generate verified certificate for course: {} - student:{} - grade: {}...".format(unicode(course.id), student, grade))
    passing_grade = Course.objects.get(key=unicode(course.id)).certificate_passing_grade
    if passing_grade is None:
        # TODO catch this exception, somewhere
        raise CertificateGenerationError(
            "Cannot assign certificate for course with no minimal certificate passing grade"
        )
    cert, _created = GeneratedCertificate.objects.get_or_create(
        user=student, course_id=course.id,
    )
    cert.name = student.profile.name

    # TODO : tests avec proctorU + logique certificats / attestation
    if grade is None or grade < passing_grade:
        cert.status = CertificateStatuses.notpassing
        logger.info("verified certificate not created, insuffisant grade, student {} not passing - grade: {} - min grade: {}...".format(student, grade, passing_grade))
    else:
        cert.status = CertificateStatuses.downloadable
        cert.download_url = ""
        # TODO: Why do we need to cast here ?
        cert.grade = '{0:.2f}'.format(grade)
        cert.mode = GeneratedCertificate.MODES.verified
        logger.info("verified certificate created for student: {}".format(student))
    cert.save()

    trigger_tracking_log(cert, course, student)

    return cert.status


class CertificateGenerationError(Exception):
    # TODO should this be here?
    pass


def create_test_certificate(course_key):
    """
    Generate the pdf certicate, save it on disk
    """

    (
        course_display_name,
        university,
        teachers, certificate_language
    ) = get_certificate_params(course_key)

    certificate_filename = make_certificate_filename(course_key, prefix="TEST_")
    certificate = CertificateInfo(settings.STUDENT_NAME_FOR_TEST_CERTIFICATE,
                                  course_display_name, university,
                                  certificate_filename, teachers,
                                  language=certificate_language)
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
                'total': 0,
                'downloadable': 0,
                'notpassing': 0
            }
    return instructor_tasks


def get_running_instructor_tasks(course_id, task_types):
    """
    Returns a query of InstructorTask objects of running tasks for a given course and task type

    Args:
        course_id (CourseKey)
        task_types (list)
    """
    instructor_tasks = InstructorTask.objects.filter(
        course_id=course_id, task_type__in=task_types
    )
    # exclude states that are "ready" (i.e. not "running", e.g. failure, success, revoked):
    for state in READY_STATES:
        instructor_tasks = instructor_tasks.exclude(task_state=state)
    return instructor_tasks.order_by('-id')


def get_teachers_list_from_course(course_key):
    """
    Return the teachers/title list attached to course
    """

    teachers = [certificate_teacher.teacher for certificate_teacher in
        CertificateTeacher.objects.filter(course__key=str(course_key)).select_related("teacher")]
    teachers_list = [u"{}/{}".format(teacher.full_name, teacher.title) for teacher in teachers]
    return teachers_list


def get_university_attached_to_course(course_id):
    """
    Get the university attached to a course return 'None' if not found

    Args:
        course_id (CourseKey)
    """
    fun_course = Course.objects.get(key=unicode(course_id))
    return fun_course.get_first_university()


def make_certificate_filename(course_id, key=None, prefix=""):
    key = key or make_certificate_hash_key()
    course_id = unicode(course_id).replace('/', '_')
    return "{}attestation_suivi_{}_{}.pdf".format(
        prefix,
        course_id,
        key
    )


def make_certificate_hash_key():
    return make_hashkey(random.random())


def set_certificate_filename(certificate, filename):
    certificate.status = CertificateStatuses.downloadable
    certificate.download_url = os.path.join(settings.CERTIFICATE_BASE_URL, filename)
    return certificate
