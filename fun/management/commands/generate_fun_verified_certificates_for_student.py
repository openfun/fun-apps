from optparse import make_option

import django
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from xmodule.modulestore.django import modulestore


from backoffice.certificate_manager.utils import generate_fun_verified_certificate
from backoffice.utils import get_course, get_course_key


class Command(BaseCommand):

    args = "<course_id user grade>"
    help = "Force the creation of a verified certficate for a student, and set her 'verified exam' grade in the certificate to the one provided."

    def handle(self, *args, **options):
        try:
            course_key_string, username, grade = args
        except ValueError:
            raise CommandError("Wrong arguments ; usage: 'course-key-string' 'user' 'grade'")

        try:
            student = User.objects.get(username=username)
        except django.contrib.auth.models.DoesNotExist:
            raise CommandError("Unknown student username: {}".format(username))

        try:
            grade = float(grade)
        except ValueError:
            raise CommandError("Grade should be a float, not: {}".format(grade))


        course_key = get_course_key(course_key_string)
        course = modulestore().get_course(course_key, depth=2)

        status = generate_fun_verified_certificate(student, course, grade)
        print("User : {} -- status : {}".format(student.username, status))
