# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
import optparse

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from microsite_configuration import microsite
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

from student.models import CourseEnrollment

from courses.models import Course


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
        """
        For each course, we create or update the corresponding
        course in Joanie through the API.
        """
        i = 0
        for course in courses:
            i += 1
            self.stdout.write('Course {}/{}: '.format(i, len(courses)), ending='')
            self.update_course(course)

        self.stdout.write('\nNumber of courses parsed: {}\n'.format(len(courses)))

    def update_course(self, course):
        """
        For the given course, we create or update the corresponding
        course in Joanie through the API.
        """
        course_id = unicode(course.id)
        self.stdout.write('Migrating data for course {}: '.format(course_id), ending='')

        joanie_hooks = getattr(settings, "JOANIE_HOOKS")
        if not joanie_hooks:
            return

        courses_hook = joanie_hooks.get('hooks', {}).get('courses')
        if not courses_hook:
            return

        edxapp_domain = microsite.get_value("site_domain", settings.LMS_BASE)
        real_course = Course.objects.get(key=course.id)
        university = real_course.get_first_university()

        data = {
            "resource_link": "https://{:s}/courses/{:s}/course".format(
                edxapp_domain, course_id
            ),
            "title": unicode(course.display_name_with_default).encode('utf-8'),
            "start": course.start and course.start.isoformat(),
            "end": course.end and course.end.isoformat(),
            "enrollment_start": course.enrollment_start
                                and course.enrollment_start.isoformat(),
            "enrollment_end": course.enrollment_end and course.enrollment_end.isoformat(),
            "languages": [real_course.language or "fr"],
            "enrollment_count": CourseEnrollment.objects.filter(course_id=course.id).count(),
            "organization_code": university.code if university else None,
        }
        json_data = json.dumps(data)

        signature = hmac.new(
            joanie_hooks["secret"].encode("utf-8"),
            msg=json_data.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        try:
            response = requests.post(
                courses_hook,
                json=data,
                headers={"Authorization": "SIG-HMAC-SHA256 {:s}".format(signature)},
                verify=joanie_hooks.get("verify", True),
                timeout=1
            )
        except requests.exceptions.ReadTimeout:
            logger.error(
                "Call to course hook timed out for {:s}".format(university_id),
                extra={"sent": data},
            )
            self.stdout.write("Error")
            return None

        if response.status_code != requests.codes.ok:
            logger.error(
                "Call to course hook failed for {:s}".format(course_id),
                extra={"sent": data, "response": response.content},
            )
            self.stdout.write("Error")
        else:
            self.stdout.write("Success")
        return None

    def handle(self, *args, **options):
        """
        This command can handle the update of a single course if the course ID
        if provided. Otherwise, it will update all courses found in MongoDB.
        """
        course_id = options.get('course_id')
        if course_id:
            course = CourseOverview.objects.get(id=course_id)
            self.update_course(course=course)
        else:
            courses = CourseOverview.objects.all()
            self.update_all_courses(courses=courses)

        print "Done !!!"
