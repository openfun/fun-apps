# pylint: disable=missing-docstring

from optparse import make_option

from django.core.management.base import BaseCommand

from backoffice.certificate_manager.verified import get_enrolled_verified_students
from backoffice.utils import get_course

from proctoru.models import ProctoruUser


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

        verified_students = get_enrolled_verified_students(course.id)
        proctoru_students = ProctoruUser.objects.filter(student__in=verified_students).values_list("student", flat=True)

        # TODO : not the best way to get students without reservations :
        #  * inscriptions in proctoru model is not bound to course (false negative)
        #  * we can't spot people who registered and cancelled their reservation
        # Thus we can fail to spot some people without reservations
        enrolled_students_not_proctoru = set(verified_students) - set(proctoru_students)

        if filename:
            with open(filename, "w") as f:
                for student in enrolled_students_not_proctoru:
                    f.write("{}\t{}\n".format(student.username, student.email))
        else:
            for student in enrolled_students_not_proctoru:
                print("{}\t{}".format(student.username, student.email))