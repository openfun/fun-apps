"""
This file contains backoffice tasks that are designed to perform background operations on the running state of a course.
"""

import os
from time import time

from certificates.models import CertificateStatuses
from instructor_task.tasks_helper import TaskProgress
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey

from ..utils_proctorU_api import get_protectU_students
from .utils import (
        generate_fun_verified_certificate,
        generate_fun_certificate,
        get_teachers_list_from_course,
        get_university_attached_to_course,
)
from .verified import get_enrolled_verified_students, get_enrolled_verified_students_count

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

    # We need to find the relevant teachers and university in case we need to
    # generate non-verified certificates.
    university = get_university_attached_to_course(course_id)
    teachers = get_teachers_list_from_course(unicode(course_id))

    # Get information from ProctorU
    proctoru_reports = get_proctoru_reports(course_id)

    for student in get_enrolled_verified_students(course_id):
        # Note that if a certificate was generated and proctoru changed its
        # accept conditions (from True to False), then the existing certificate
        # will probably not be removed.
        proctoru_student_reports = proctoru_reports.get(student.username, [])
        if is_proctoru_ok(proctoru_student_reports):
            student_status = generate_fun_verified_certificate(student, course)
            if student_status == CertificateStatuses.notpassing:
                # Attempt to generate non-verified certificate
                student_status = generate_fun_certificate(
                    student, course,
                    teachers, university,
                )
        else:
            student_status = generate_fun_certificate(
                student, course,
                teachers, university,
            )
        yield student_status

def is_proctoru_ok(proctoru_student_reports):
    """Check ProctorU accept conditions from the reports

    As a debug feature, this function will return True for all students when
    the PROCTORU_ALL_STUDENTS_OK environment variable is defined. This is a
    temporary measure that should be removed when we don't need it anymore.
    (i.e: when we have found a way to abstract ourselves from the ProctorU API)
    """
    if os.environ.get("PROCTORU_ALL_STUDENTS_OK"):
        return True

    if len(proctoru_student_reports) > 0:
        first_report = proctoru_student_reports[0]
        return (
            first_report.get("Authenticated") and
            first_report.get("TestSubmitted") and
            not first_report["Escalated"] and
            not first_report.get("IncidentReport")
        )
    else:
        return False


def get_proctoru_reports(course_id):
    """
    Get the proctorU reports for this course for all users.

    Returns:
        {
            student1_username: [reports],
            student2_username: [reports],
        }
    """
    ck = CourseKey.from_string(unicode(course_id))
    registered_users = get_protectU_students(course_name=ck.course, course_run=ck.run, student_grades=None)
    return registered_users
