from pprint import pprint
from optparse import make_option
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from django.db import models
from backoffice import utils_proctorU_api
from student.models import CourseEnrollment

from backoffice.certificate_manager.verified import enrolled_proctoru_students
from opaque_keys.edx.keys import CourseKey

from certificates.models import certificate_status_for_student


class Command(BaseCommand):
    help = 'Get proctoru and certificate infos for a given course.'
    args = '< course_key_string >'

    option_list = BaseCommand.option_list + (
        make_option("--course_key_string",
            help='CourseKeyString of the course to analyse'),
    )

    def handle(self, *args, **options):
        course_key_string = args[0]
        course_id = CourseKey.from_string(course_key_string)
        student_ids = enrolled_proctoru_students(course_id)

        reports = utils_proctorU_api.get_reports_from_ids(course_id.course, course_id.run, student_ids=student_ids)

        for student in reports:
            user = User.objects.get(username=student)
            course_enrollment = CourseEnrollment.objects.get(course_id=course_id, user=user)
            generated_certificate = certificate_status_for_student(user, course_id)

            print("Previous certificate status: {}".format(generated_certificate.get("status")))
            print("Mode for student {}: {}".format(student, course_enrollment.mode))
            print("reports for: {} -- is OK PU: {}".format(student, utils_proctorU_api.is_proctoru_ok(reports[student])))
            pprint(reports[student])
