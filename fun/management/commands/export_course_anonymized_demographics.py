# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from optparse import make_option
from student.models import UserProfile
from xmodule.modulestore.django import modulestore
import hashlib
import hmac
import json


class Command(BaseCommand):
    help = """Gather demographics from a course_id, anonymize users and prints the result as a JSON"""
    option_list = BaseCommand.option_list + (
        make_option('--course_id', action='store', dest='COURSE_ID', type='string'),
    )

    def handle(self, *args, **options):
        if not options['COURSE_ID']:
            raise CommandError('--course_id mandatory')
        try:
            course_key = CourseKey.from_string(options['COURSE_ID'])
            if not modulestore().get_course(course_key, depth=2):
                raise ValueError()
        except InvalidKeyError:
            raise CommandError("Course id {} could not be parsed as a CourseKey;".format(options['COURSE_ID']))
        except ValueError:
            raise CommandError("\n Course {} not found.".format(options['COURSE_ID']))
        # gathers demographic data for course students
        demographics = UserProfile.objects.filter(user__courseenrollment__course_id=course_key)
        json_data = {
            "demographic": [self.profile_demographics(profile) for profile in demographics]
        }
        self.stdout.write(json.dumps(json_data, indent=2))
        self.stdout.write("\n")

    def profile_demographics(self, profile):
        anonymized_username = hmac.new(
            settings.ANONYMIZATION_KEY, str(profile.user), hashlib.sha256
        ).hexdigest()
        return {
            'username': anonymized_username,
            'gender': profile.gender,
            'year_of_birth': profile.year_of_birth,
            'level_of_education': profile.level_of_education,
            'country': str(profile.country)
        }
