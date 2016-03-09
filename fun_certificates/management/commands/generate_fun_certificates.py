# Python modules
import datetime
from pytz import UTC
from pprint import pprint
from optparse import make_option

# Django modules
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

# edX modules
from certificates.models import (
  certificate_status_for_student,
  CertificateStatuses as status)

from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

from backoffice.certificate_manager.utils import get_certificate_params, generate_fun_certificate


class Command(BaseCommand):

    help = """
    Find all students that need certificates for courses that have finished and
    put their cert requests on the queue.

    If --user is given, only grade and certify the requested username.
    """

    option_list = BaseCommand.option_list + (
        make_option('-c', '--course',
                    metavar='COURSE_ID',
                    dest='course',
                    help='Grade and generate certificates '
                    'for a specific course'),
        make_option('-t', '--teacher',
                    action='append',
                    metavar='TEACHERNAME',
                    dest='teachers',
                    default=[],
                    help='Specify the name of a teacher to include in the certificate. '
                    'Up to four names can be specified.'),
        make_option('-i', '--ignore-grades',
                    action='store_true',
                    dest='ignore_grades',
                    default=False,
                    help='Ignore grades.'),
        make_option('--fail',
                    action='store_true',
                    dest='fail',
                    default=False,
                    help='arbitrary set the certificate status to notpassing'),
        make_option('-s', '--set-grade',
                    metavar='GRADE',
                    dest='grade',
                    default=None,
                    help='set a new grade.'),
        make_option('-f', '--force',
                    action='store_true',
                    dest='force',
                    default=False,
                    help='(re)generate all certificates'),
        make_option('-u', '--user',
                    metavar='USERNAME',
                    dest='user',
                    default=None,
                    help='The username or email address for whom grading and certification should be requested'),
    )

    def handle(self, *args, **options):
        # Will only generate a certificate if the current
        # status is in the unavailable state, can be set
        # to something else with the force flag

        if len(options['teachers']) > 4:
            raise CommandError("Too many teachers. Certificate can not include more than four names.")
        if not options['course']:
            raise CommandError("--course argument is mandatory")
        if options['grade'] and float(options['grade']) > 1:
            raise CommandError('grades range from 0 to 1')

        try:
            ended_courses = [CourseKey.from_string(options['course'])]
        except InvalidKeyError:
            raise CommandError("Course id {} could not be parsed as a CourseKey;".format(options['course']))

        for course_id in ended_courses:
            # prefetch all chapters/sequentials by saying depth=2

            (course, course_display_name, university, logo_path,
                    certificate_base_filename, _, _) = get_certificate_params(course_id)

            print "Fetching enrolled students for {0} ()".format(course_id)
            enrolled_students = get_enrolled_students(course_id, options['user'])
            total = enrolled_students.count()
            print "Course has {0} enrolled students".format(total)
            stats = {
                status.notpassing: 0,
                status.error: 0,
                status.downloadable: 0
            }
            start = datetime.datetime.now(UTC)

            for count, student in enumerate(enrolled_students):
                start = print_progress(count, total, start)
                if options['force'] or (certificate_status_for_student(student, course_id)['status'] != status.downloadable):
                    new_status = generate_fun_certificate(
                        student, course_id, course_display_name, course,
                        options['teachers'], university.name, logo_path,
                        certificate_base_filename, options['ignore_grades'], options['grade'], options['fail'])
                    stats[new_status] += 1
                    pprint(stats)

def get_enrolled_students(course_id, user_identification=None):
    query_args = {
        "courseenrollment__course_id": course_id,
        "profile__isnull": False
    }
    if user_identification is not None:
        if '@' in user_identification:
            query_args["email"] = user_identification
        else:
            query_args["username"] = user_identification
    return User.objects.filter(**query_args).prefetch_related("groups").order_by('username')

def print_progress(count, total, start):
    # Print update after this many students
    STATUS_INTERVAL = 100

    if count % STATUS_INTERVAL == 0:
        # Print a status update with an approximation of
        # how much time is left based on how long the last
        # interval took
        diff = datetime.datetime.now(UTC) - start
        timeleft = diff * (total - count) / STATUS_INTERVAL
        hours, remainder = divmod(timeleft.seconds, 3600)
        minutes, _seconds = divmod(remainder, 60)
        print "{0}/{1} completed ~{2:02}:{3:02}m remaining".format(
            count, total, hours, minutes)
        start = datetime.datetime.now(UTC)
    return start
