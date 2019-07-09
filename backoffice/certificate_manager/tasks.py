"""
This file contains backoffice tasks that are designed to perform background operations on the running state of a course.
"""

from time import time
import logging

from django.contrib.auth.models import User

from instructor_task.tasks_helper import TaskProgress
from xmodule.modulestore.django import modulestore
from certificates.models import (
  certificate_status_for_student,
  CertificateStatuses as status,
)
from student.models import CourseEnrollment

from .utils import (
        generate_fun_verified_certificate,
        create_test_certificate,
        generate_fun_certificate,
        get_teachers_list_from_course,
        get_university_attached_to_course,
)

logger = logging.getLogger(__name__)

def generate_certificate(_xmodule_instance_args, _entry_id, course_id, _task_input, action_name):
    """
    Function called by the instructor task API for certificate generation
    """
    return generate_course_certificates(course_id, action_name)

def generate_course_certificates(course_id, action_name):
    """
    Generate course certificates while monitoring the progress in the admin in
    a TaskProgress object.
    """
    # generate a test certificate
    test_certificate = create_test_certificate(course_id)

    # generate real certificate for students
    task_progress = TaskProgress(action_name, get_enrolled_students_count(course_id), time())

    progress_status = {
        status.notpassing: 0,
        status.error: 0,
        status.downloadable: 0,
        'test_certificate_filename': test_certificate.filename
    }

    task_progress.update_task_state(extra_meta=progress_status)
    for student_status in iter_generated_course_certificates(course_id):
        task_progress.attempted += 1
        if student_status is None:
            task_progress.skipped += 1
        else:
            task_progress.succeeded += 1
        progress_status[student_status] += 1
        task_progress.update_task_state(extra_meta=progress_status)
    return task_progress.update_task_state(extra_meta=progress_status)

def iter_generated_course_certificates(course_id):
    """
    Iterate on the certificates generated for all students that graduated from
    the course. Certificates are regenerated when necessary i.e: when the pdf
    file does not already exist.

    Args:
        course_id (CourseKey)
    Yields:
        status (str): one of CertificateStatuses. Yields None if the
            certificate was skipped.
    """

    course = modulestore().get_course(course_id, depth=2)
    university = get_university_attached_to_course(course_id)
    teachers = get_teachers_list_from_course(unicode(course_id))

    for student in get_enrolled_students(course_id):
        logger.info("processing certificate for student: {}".format(student))
        course_enrollment = CourseEnrollment.objects.get(course_id=course_id, user=student)

        student_status = status.notpassing

        if course_enrollment.mode == 'verified':
            logger.info("generating fun verified certificate for {}: {}".format(student.username, unicode(course)))
            student_status = generate_fun_verified_certificate(student, course)

        if course_enrollment.mode == 'honor' or student_status == status.notpassing:
            logger.info("generating fun honor certificate for {}: {}".format(student.username, unicode(course)))
            student_status = generate_fun_certificate(
                student, course,
                teachers, university,
            )

        else:
            message = "Unknown course mode for {}: {}".format(student.username, course_enrollment.mode)
            logger.error(message)

        yield student_status

def get_enrolled_students_count(course_id):
    return get_enrolled_students(course_id).count()

def get_enrolled_students(course_id):
    return User.objects.filter(
        courseenrollment__course_id=course_id, profile__isnull=False
    ).prefetch_related("groups").order_by('username')
