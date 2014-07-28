# pylint: disable=missing-docstring

import csv
import json
import datetime
from pytz import UTC

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from certificates.models import GeneratedCertificate
from certificates.models import CertificateStatuses as status
from student.models import UserProfile
from student.models import CourseEnrollment
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from opaque_keys.edx.keys import CourseKey

##
##  Csv functions
##

def cleanup_newlines(s):
    """Makes sure all the newlines in s are representend by \r only."""
    return s.replace("\r\n","\r").replace("\n","\r")

def return_csv(header_row, data_rows, filename, start_time):
    """Outputs a CSV file from the contents of a datatable."""
    ofile  = open(filename, "wb")
    writer = csv.writer(ofile, dialect='excel', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(header_row)
    for datarow in data_rows:
        encoded_row = [cleanup_newlines(unicode(s).encode('utf-8')) for s in datarow]
        writer.writerow(encoded_row)
    ofile.close()
    print "Operation succeed, {0} has just been created, operation lasted {1}".format(
        filename, datetime.datetime.now(UTC) - start_time)

class Command(BaseCommand):
    help = """
        Command that will give for each user which mooc he suscribed to,
and if he got the certification. Below the csv structure :
          user_id  | registration date     | mooc A            | mooc B      | mooc C         | ...

           01      | 4/05/2014             |  NON REGISTERED   | SUCCEED     | FAILED
           02
           ...
          """

    def get_courses(self):
        """Return a list of all courses"""
        store = modulestore()
        return store.get_courses()

    def create_header_row(self, course_ids):
        """return the header row of the csv"""
        header_row = ['id', 'registration date']
        return header_row + course_ids

    def check_certification(self, user, course_id):
        """return the certificate status for a particular user"""
        try:
           certificate = GeneratedCertificate.objects.get(user=user, course_id=course_id)
           if certificate.status == status.downloadable:
               return 'SUCCEED'
           elif certificate.status == status.notpassing:
               return 'FAILED'
           else:
               return certificate.status
        except GeneratedCertificate.DoesNotExist:
            return 'NOT GRADED'

    def handle(self, *args, **options):

        courses = self.get_courses()
        course_ids = [course.id.to_deprecated_string() for course in courses]
        header_row = self.create_header_row(course_ids)

        data_rows = []
        data_row = []

        students = UserProfile.objects.all()

        print ( "The command has just begun, please wait")
        start_time = datetime.datetime.now(UTC)

        for student in students:
            data_row = [student.id, student.user.date_joined.strftime("%d-%m-%Y")]
            for course in courses:
                #print(course.id._key)
                try:
                    courses_enrolled = CourseEnrollment.objects.get(user=student.user, course_id=course.id,
                                                                     user__is_superuser=False)
                    certification = self.check_certification(student.user, course.id)
                    data_row.append(certification)
                except CourseEnrollment.DoesNotExist:
                    data_row.append('NOT REGISTERED')
            data_rows.append(data_row)
        return_csv(header_row, data_rows, "/tmp/moocs_registrations.csv", start_time)
