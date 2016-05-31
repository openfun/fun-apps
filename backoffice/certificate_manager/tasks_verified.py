"""
This file contains backoffice tasks that are designed to perform background operations on the running state of a course.
"""

from time import time
import logging

from certificates.models import CertificateStatuses
from instructor_task.tasks_helper import TaskProgress
from xmodule.modulestore.django import modulestore
from backoffice.certificate_manager.verified import enrolled_proctoru_students

from ..utils_proctorU_api import get_reports_from_ids, is_proctoru_ok
from .utils import (
        generate_fun_verified_certificate,
        generate_fun_certificate,
        get_teachers_list_from_course,
        get_university_attached_to_course,
)
from .verified import get_enrolled_verified_students, get_enrolled_verified_students_count

logger = logging.getLogger(__name__)


def generate_verified_certificate(_xmodule_instance_args, _entry_id, course_id, _task_input, action_name):
    """
    Function called by the instructor task API for certificate generation
    """
    return generate_course_verified_certificates(course_id, action_name)


def generate_course_verified_certificates(course_id, action_name):
    """
    Generate course certificates while monitoring the progress in the admin in
    a TaskProgress object.
    """
    # generate real certificates for students
    task_progress = TaskProgress(action_name, get_enrolled_verified_students_count(course_id), time())

    progress_status = {
        CertificateStatuses.notpassing: 0,
        CertificateStatuses.error: 0,
        CertificateStatuses.downloadable: 0,
    }

    task_progress.update_task_state(extra_meta=progress_status)
    for student_status in iter_generated_course_verified_certificates(course_id):
        task_progress.attempted += 1
        if student_status is None:
            task_progress.skipped += 1
        else:
            task_progress.succeeded += 1
        progress_status[student_status] += 1
        task_progress.update_task_state(extra_meta=progress_status)
    return task_progress.update_task_state(extra_meta=progress_status)


def iter_generated_course_verified_certificates(course_id):
    """
    Iterate on students enrolled to verified certificate for the course.
    Certificates are regenerated if all conditions are ok. Proctoru validated the exam
    and grade is good enough, if not a pdf certificate is generated.

    Args:
        course_id (CourseKey)
    Yields:
        status (str): one of CertificateStatuses. Yields None if the
            certificate was skipped.
    """

    course = modulestore().get_course(course_id, depth=2)

    # We need to find the relevant teachers and university in case we need to
    # generate non-verified certificates.
    university = get_university_attached_to_course(course_id)
    teachers = get_teachers_list_from_course(unicode(course_id))

    # Get information from ProctorU
    # today = datetime.datetime.today()
    # begin = today - datetime.timedelta(300)
    student_ids = enrolled_proctoru_students(course_id)
    proctoru_reports = get_reports_from_ids(course_id.course, course_id.run, student_ids=student_ids)

    for student in get_enrolled_verified_students(course_id):
        # Note that if a certificate was generated and proctoru changed its
        # accept conditions (from True to False), then the existing certificate
        # will probably not be removed.
        proctoru_student_reports = proctoru_reports.get(student.username, [])
        logger.info("report for verified student {}: {}".format(student.username, proctoru_student_reports))
        if is_proctoru_ok(proctoru_student_reports):
            logger.info("proctoru ok for student: {}".format(student.username))
            student_status = generate_fun_verified_certificate(student, course)
            if student_status == CertificateStatuses.notpassing:
                # Attempt to generate non-verified certificate
                student_status = generate_fun_certificate(
                    student, course,
                    teachers, university,
                )
        else:
            logger.info("proctoru fail for student: {}".format(student.username))
            student_status = generate_fun_certificate(
                student, course,
                teachers, university,
            )
        yield student_status
