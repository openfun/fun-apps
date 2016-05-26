# pylint: disable=missing-docstring

from optparse import make_option
import sys

from django.core.management.base import BaseCommand

from backoffice.certificate_manager.verified import get_enrolled_verified_students
from backoffice.utils import get_course_key, get_course
from backoffice import utils_proctorU_api

class Command(BaseCommand):

    # def add_arguments(self, parser):
    #     parser.add_argument('--filename', type=str, help='filename where the output will be written')
    #     parser.add_argument('course_key_string', type=str, help='CourseKeyString of the course to analyse')
    option_list = BaseCommand.option_list + (
        make_option('--filename',
                    default=False,
            help='File where the output will be written / defaults to stdout when not provided'),
        make_option("--course_key_string",
            help='CourseKeyString of the course to analyse'),
        make_option('--proctoru_endpoint',
                    default=False,
            help='Proctoru endpoint to reach / defaults to the one in config'),
        make_option('--proctoru_token',
                    default=False,
            help='Proctoru token to use / defaults to the one in config'),

    )

    def handle(self, filename, course_key_string, proctoru_endpoint, proctoru_token, *args, **options):
        course_key = get_course_key(course_key_string)
        verified_students = get_enrolled_verified_students(course_key)

        course = get_course(course_key_string)
        proctoru_reports = utils_proctorU_api.get_proctorU_students(
            #course_name=course.id.course, course_run=course.id.run
            course_name="FUN103", course_run="FUNV3", endpoint=proctoru_endpoint, token=proctoru_token
        )
        if "warn" in proctoru_reports:
            sys.exit("ProctorU is empty for this course, is everything OK?")
        if "error" in proctoru_reports:
            sys.exit(proctoru_reports["error"])

        proctoru_users = [reports[0]["user"] for reports in proctoru_reports]

        enrolled_students_not_proctoru = set(verified_students) - set(proctoru_users)

        if filename:
            with open(filename, "w") as f:
                for student in enrolled_students_not_proctoru:
                    f.write("{}\t{}\n".format(student.username, student.email))
        else:
            for student in enrolled_students_not_proctoru:
                print("{}\t{}".format(student.username, student.email))
