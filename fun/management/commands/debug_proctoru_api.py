from pprint import pprint
from optparse import make_option
from django.core.management.base import BaseCommand
from django.db import models
from backoffice import utils_proctorU_api
from backoffice.certificate_manager.verified import enrolled_proctoru_students
from opaque_keys.edx.keys import CourseKey


class Command(BaseCommand):
    help = 'get the proctoru infos for a given course'

    option_list = BaseCommand.option_list + (
        make_option('--begin',
                    help='date of the beginning of the request'),
        make_option('--end',
                    help='date of the end of the request'),
        make_option("--course_key_string",
            help='CourseKeyString of the course to analyse'),
    )

    def handle(self, *args, **options):
        begin = models.DateField().to_python(options["begin"])
        end = models.DateField().to_python(options["end"])
        course_id = CourseKey.from_string(options["course_key_string"])
        student_ids = enrolled_proctoru_students(course_id)

        #reports = utils_proctorU_api.get_proctorU_students(course_id.course, course_id.run, begin, request_end_date = end, student_grades=None)
        reports = utils_proctorU_api.get_proctorU_students(course_id.course, course_id.run,
                                                           student_ids=student_ids,
                                                           student_grades=None)
        pprint(reports)