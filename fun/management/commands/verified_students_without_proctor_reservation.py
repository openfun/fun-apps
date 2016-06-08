# pylint: disable=missing-docstring

import csv
from optparse import make_option
import sys

from django.core.management.base import BaseCommand

from backoffice.certificate_manager.verified import get_enrolled_verified_students
from backoffice.utils import get_course

from proctoru.models import ProctoruUser


def write_csv(file_handler, header, rows):
    writer = csv.writer(file_handler)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--filename',
                    default=False,
            help='File where the output will be written / defaults to stdout when not provided'),
        make_option("--course_key_string",
            help='CourseKeyString of the course to analyse'),
    )

    def handle(self, filename, course_key_string, *args, **options):
        course = get_course(course_key_string)

        verified_students = get_enrolled_verified_students(course.id).select_related("profile")
        proctoru_students = ProctoruUser.objects.filter(student__in=verified_students).values_list("student", flat=True)

        # TODO : not the best way to get students without reservations :
        #  * inscriptions in proctoru model is not bound to course (false negative)
        #  * we can't spot people who registered and cancelled their reservation
        # Thus we can fail to spot some people without reservations
        enrolled_students_not_proctoru = set(verified_students) - set(proctoru_students)

        header = ("Student name", "Username", "Email")
        rows = [(s.profile.name, s.username, s.email) for s in enrolled_students_not_proctoru]

        if filename:
            with open(filename, "w") as f:
                write_csv(f, header, rows)
        else:
            write_csv(sys.stdout, header, rows)
