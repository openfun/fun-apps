"""
This file contains backoffice tasks that are designed to perform background operations on the running state of a course.
"""

import os
from time import time

from django.contrib.auth.models import User

from instructor_task.tasks_helper import TaskProgress
from xmodule.modulestore.django import modulestore
from certificates.models import (
  certificate_status_for_student,
  CertificateStatuses as status,
)

from backoffice.certificate_manager.utils import (
    get_teachers_list_from_course, create_test_certificate, get_university_attached_to_course,
    generate_fun_certificate)


def generate_certificate(_xmodule_instance_args, _entry_id, course_id, _task_input, action_name):
    generate_course_certificates(course_id, action_name)

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
        'test_certificate_filename' : test_certificate.filename
    }

    for student_status in iter_generated_course_certificates(course_id):
        task_progress.attempted += 1
        if student_status == status.downloadable:
            task_progress.skipped += 1
        else:
            task_progress.succeeded += 1
        progress_status[student_status] += 1
        task_progress.update_task_state(extra_meta=progress_status)

def iter_generated_course_certificates(course_id):
    """
    Generate a certificate for all students that graduated from the course

    Args:
        course_id (CourseKey)
        action_name (str): some string to monitor the task progress
    """

    course = modulestore().get_course(course_id, depth=2)
    course_display_name = unicode(course.display_name).encode('utf-8')
    university = get_university_attached_to_course(course)
    certificate_base_filename = "attestation_suivi_" + (course_id.to_deprecated_string().replace('/', '_')) + '_'

    teachers = get_teachers_list_from_course(unicode(course_id))

    for student in get_enrolled_students(course_id):
        if certificate_status_for_student(student, course_id)['status'] != status.downloadable:
            if university.certificate_logo:
                logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
            else:
                logo_path = None
            student_status = generate_fun_certificate(
                student, course_id,
                course_display_name, course,
                teachers, university.name,
                logo_path, certificate_base_filename,
                False, False, False
            )
            yield student_status
        else:
            yield status.downloadable

def get_enrolled_students_count(course_id):
    return get_enrolled_students(course_id).count()

def get_enrolled_students(course_id):
    return User.objects.filter(
        courseenrollment__course_id=course_id, profile__isnull=False
    ).prefetch_related("groups").order_by('username')

