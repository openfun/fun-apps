# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
import optparse

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from microsite_configuration import microsite

from student.models import CourseEnrollment

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update FUN's course data."
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            '--course-id',
            action='store',
            type='string',
            dest='course_id',
            default='',
            help='Update only the given course.',
        ),
    )

    def update_all_courses(self, courses):
        '''
        For each course, we create or update the corresponding
        course in SQL Course table.
        '''
        for course in courses:
            try:
                self.update_course(
                    modulestore().get_course(course.id),
                )
            except InvalidKeyError as err:
                # Log the error but continue indexing other courses
                logger.error(err)

        self.stdout.write('Number of courses parsed: {}\n'.format(len(courses)))
        return None

    def update_course(self, course):
        '''
        For the given course, we create or update the corresponding
        course in SQL Course table.
        '''

        # course_handler = CourseHandler(mongo_course)
        course_id = unicode(course.id)
        self.stdout.write('\nMigrating data for course {}\n'.format(course_id))
        # update_courses_meta_data(course_id=unicode(key))

        joanie_hooks = getattr(settings, "JOANIE_HOOKS")
        if not joanie_hooks:
            return

        courses_hook = joanie_hooks.get('hooks', {}).get('courses')
        if not courses_hook:
            return

        # Synchronize with external course hook
        # course_id = kwargs["course_id"]
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key)
        edxapp_domain = microsite.get_value("site_domain", settings.LMS_BASE)

        data = {
            "resource_link": "https://{:s}/courses/{:s}/info".format(
                edxapp_domain, course_id
            ),
            "title": unicode(course.display_name_with_default).encode('utf-8'),
            "start": course.start and course.start.isoformat(),
            "end": course.end and course.end.isoformat(),
            "enrollment_start": course.enrollment_start
                                and course.enrollment_start.isoformat(),
            "enrollment_end": course.enrollment_end and course.enrollment_end.isoformat(),
            "languages": [course.language or "fr"],
            "enrollment_count": CourseEnrollment.objects.filter(course_id=course_key).count()
        }
        json_data = json.dumps(data)
        print(json_data)

        signature = hmac.new(
            joanie_hooks["secret"].encode("utf-8"),
            msg=json_data.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        response = requests.post(
            courses_hook,
            json=data,
            headers={"Authorization": "SIG-HMAC-SHA256 {:s}".format(signature)},
            verify=joanie_hooks.get("verify", True),
        )
        print(response.json())

        if response.status_code != requests.codes.ok:
            logger.error(
                "Call to course hook failed for {:s}".format(course_id),
                extra={"sent": data, "response": response.content},
            )
        
        self.stdout.write('Migrated course {}\n'.format(course_id))
        return None

    def handle(self, *args, **options):
        '''
        This command can handle the update of a single course if the course ID
        if provided. Otherwise, it will update all courses found in MongoDB.
        '''
        course_id = options.get('course_id')
        if course_id:
            # course_key is a CourseKey object and course_id its sting representation
            course_key = CourseKey.from_string(course_id)
            course = modulestore().get_course(course_key)
            self.update_course(
                course=course,
            )
        else:
            courses = modulestore().get_courses()
            self.update_all_courses(
                courses=courses,
            )

        print "Done !!!"
