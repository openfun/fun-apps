# Python modules
import os
import datetime
from pytz import UTC
from pprint import pprint
from optparse import make_option
import random

# Django modules
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.auth.models import User
from django.test.client import RequestFactory

# edX modules
from courseware import grades
from xmodule.modulestore.django import modulestore
from certificates.models import (
  certificate_status_for_student,
  CertificateStatuses as status,
  GeneratedCertificate)
from fun_certificates.generator import CertificateInfo
from student.models import UserProfile
from capa.xqueue_interface import make_hashkey
from universities.models import University

from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

factory = RequestFactory()
request = factory.get('/')
request.session = {}


def generate_fun_certificate(
    student, course_id,
    course_display_name, course,
    teachers,
    organization_display_name, organization_logo,
    certificate_base_filename, ignore_grades, new_grade
):
    """Generates a certificate for one student and one course."""

    profile = UserProfile.objects.get(user=student)
    student_name = unicode(profile.name).encode('utf-8')
    # grade the student
    cert, _created = GeneratedCertificate.objects.get_or_create(
        user=student, course_id=course_id
    )

    request.user = student
    grade = grades.grade(student, request, course)
    cert.grade = grade['percent']
    cert.user = student
    cert.course_id = course_id
    cert.name = profile.name

    if ignore_grades:
        grade['grade'] = 'A'
        grade['percent'] = 100.0

    if new_grade:
        grade['grade'] = 'A'
        cert.grade = new_grade
        cert.save()

    if grade['grade'] is None:
        cert.status = status.notpassing
    else:
        key = make_hashkey(random.random())
        cert.key = key
        certificate_filename = certificate_base_filename + key + ".pdf"
        info = CertificateInfo(
            student_name, course_display_name,
            organization_display_name, organization_logo,
            certificate_filename, teachers
        )
        info.generate()

        cert.status = status.downloadable
        cert.download_url = settings.CERTIFICATE_BASE_URL + certificate_filename
    cert.save()
    return cert.status

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
                    default=False,
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
            print "Too many teachers. Certificate can not include more than four names."
            return

        # Print update after this many students

        STATUS_INTERVAL = 100

        if options['course']:
            try:
                ended_courses = [CourseKey.from_string(options['course'])]
            except InvalidKeyError:
                print("Course id {} could not be parsed as a CourseKey;".format(options['course']))
                return

        if options['grade'] and float(options['grade']) > 1:
            raise CommandError('grades range from 0 to 1')

        for course_id in ended_courses:
            # prefetch all chapters/sequentials by saying depth=2
            course = modulestore().get_course(course_id, depth=2)
            course_display_name = unicode(course.display_name).encode('utf-8')
            university = University.objects.get(code=course.location.org)
            certificate_base_filename = "attestation_suivi_" + (course_id.to_deprecated_string().replace('/', '_')) + '_'
            print "Fetching enrolled students for {0} ()".format(course_id)
            if options['user'] is None:
                enrolled_students = User.objects.filter(
                    courseenrollment__course_id=course_id, profile__isnull=False).prefetch_related(
                    "groups").order_by('username')
            else:
                user = options['user']
                query_args = {
                    "courseenrollment__course_id": course_id,
                    "profile__isnull": False
                }
                if '@' in user:
                    query_args["email"] = user
                else:
                    query_args["username"] = user
                enrolled_students = User.objects.filter(**query_args)
            total = enrolled_students.count()
            print "Course has {0} enrolled students".format(total)
            count = 0
            stats = {
                status.notpassing : 0,
                status.error : 0,
                status.downloadable : 0
            }
            start = datetime.datetime.now(UTC)

            for student in enrolled_students:
                count += 1
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
                if options['force'] or (certificate_status_for_student(student, course_id)['status'] != status.downloadable):
                    if university.certificate_logo:
                        logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
                    else:
                        logo_path = None
                    new_status = generate_fun_certificate(
                        student, course_id, course_display_name, course,
                        options['teachers'], university.name, logo_path,
                        certificate_base_filename, options['ignore_grades'], options['grade']
                    )
                    stats[new_status] += 1
                    pprint(stats)
