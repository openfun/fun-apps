# pylint: disable=missing-docstring

from optparse import make_option

from django.core.management.base import BaseCommand

from xmodule.modulestore.django import modulestore

from backoffice.certificate_manager.verified import get_enrolled_verified_students
from backoffice.utils import get_course_key, get_course
from backoffice.utils_proctorU_api import get_verified_students_without_proctoru_reservations

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
        make_option('--proctoru_base',
                    default=False,
            help='Proctoru base url to reach / defaults to the one in config'),
        make_option('--proctoru_token',
                    default=False,
            help='Proctoru token to use / defaults to the one in config'),

    )

    def handle(self, filename, course_key_string, proctoru_base, proctoru_token, *args, **options):
        enrolled_students_not_proctoru = get_verified_students_without_proctoru_reservations(course_key_string,
                                                                                             proctoru_base,
                                                                                             proctoru_token)

        if filename:
            with open(filename, "w") as f:
                for student in enrolled_students_not_proctoru:
                    f.write("{}\t{}\n".format(student.username, student.email))
        else:
            for student in enrolled_students_not_proctoru:
                print("{}\t{}".format(student.username, student.email))
