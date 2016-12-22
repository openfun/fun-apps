# pylint: disable=missing-docstring

import csv
import logging
from optparse import make_option
import sys

from django.core.management.base import BaseCommand, CommandError

from student.models import User

from backoffice.certificate_manager.verified import get_enrolled_verified_students
from backoffice.utils import get_course

logger = logging.getLogger(__name__)

try:
    INSTALLED_PU = True
    from proctoru.models import ProctoruUser
except ImportError:
    logger.info("ProcotorU XBlock not installed")
    INSTALLED_PU = False


def write_csv(file_handler, header, rows):
    writer = csv.writer(file_handler)
    writer.writerow(header)
    for row in rows:
        writer.writerow([s.encode("utf8") for s in row])


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--filename',
                    default=False,
            help='File where the output will be written / defaults to stdout when not provided'),
        make_option("--course-key-string",
            help='CourseKeyString of the course to analyse'),
    )

    def handle(self, *args, **options):
        if options["course_key_string"]:
            course_key_string = options["course_key_string"]
        else:
            raise CommandError("Option `--course-key-string=...` must be specified.")

        course = get_course(course_key_string)

        verified_students = get_enrolled_verified_students(course.id).select_related("profile")
        if INSTALLED_PU:
            proctoru_registered_user = ProctoruUser.objects.filter(student__in=verified_students)
        else:
            proctoru_registered_user = []
        students_registered_in_proctoru = User.objects.filter(proctoruuser__in=proctoru_registered_user)

        # TODO : not the best way to get students without reservations :
        #  * inscriptions in proctoru model is not bound to course (false negative)
        #  * we can't spot people who registered and cancelled their reservation
        # Thus we can fail to spot some people without reservations
        enrolled_students_not_proctoru = set(verified_students) - set(students_registered_in_proctoru)

        header = ("Name", "Username", "Email")
        rows = [(s.profile.name, s.username, s.email) for s in enrolled_students_not_proctoru]

        if options['filename']:
            with open(options['filename'], "w") as f:
                write_csv(f, header, rows)
        else:
            write_csv(sys.stdout, header, rows)
