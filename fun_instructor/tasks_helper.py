"""
This file contains tasks that are designed to perform background operations on the running state of a course.
"""
from datetime import datetime
from time import time
from pytz import UTC
import os

from instructor_task.tasks_helper import TaskProgress
from xmodule.modulestore.django import modulestore
from certificates.models import (
  certificate_status_for_student,
  CertificateStatuses as status,
  GeneratedCertificate)

from fun_certificates.management.commands.generate_fun_certificates import get_enrolled_students, generate_fun_certificate

from universities.models import University


def generate_certificate(_xmodule_instance_args, _entry_id, course_id, _task_input, action_name):
    """ """

    course = modulestore().get_course(course_id, depth=2)
    course_display_name = unicode(course.display_name).encode('utf-8')
    university = University.objects.get(code=course.location.org)
    certificate_base_filename = "attestation_suivi_" + (course_id.to_deprecated_string().replace('/', '_')) + '_'


    start_time = time()
    start_date = datetime.now(UTC)
    status_interval = 1
    enrolled_students = get_enrolled_students(course_id)
    task_progress = TaskProgress(action_name, enrolled_students.count(), start_time)

    all_status = {status.notpassing: 0,
                    status.error: 0,
                    status.downloadable: 0,}

    for count, student in enumerate(enrolled_students):
        if task_progress.attempted % status_interval == 0:
            task_progress.update_task_state(extra_meta=all_status)
        task_progress.attempted += 1
        if certificate_status_for_student(student, course_id)['status'] != status.downloadable:
            if university.certificate_logo:
                logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
            else:
                logo_path = None
            student_status = generate_fun_certificate(student, course_id,
                                                  course_display_name, course,
                                                  ["henri/prof"], university.name,
                                                  logo_path, certificate_base_filename,
                                                  False, False, False)
            if student_status:
                all_status[student_status] += 1
                task_progress.succeeded += 1
            else:
                task_progress.failed += 1
    return task_progress.update_task_state(extra_meta=all_status)

