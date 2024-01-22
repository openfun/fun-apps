# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
from pprint import pprint

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from microsite_configuration import microsite
from opaque_keys.edx.keys import CourseKey

from student.models import CourseEnrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update FUN's course data."

    def update_enrollment(self, enrollment):
        enrollment_id = unicode(enrollment.id)
        self.stdout.write('Migrating data for enrollment {}: '.format(enrollment_id), ending='')
        if not enrollment.course_overview:
            self.stdout.write("No course overview")
            return None

        joanie_hooks = getattr(settings, "JOANIE_HOOKS")
        if not joanie_hooks:
            return

        enrollments_hook = joanie_hooks.get('hooks', {}).get('enrollments')
        if not enrollments_hook:
            return

        edxapp_domain = microsite.get_value("site_domain", settings.LMS_BASE)
        data = {
            "resource_link": "https://{:s}/courses/{:s}/course".format(
                edxapp_domain, enrollment.course_id
            ),
            "is_active": enrollment.is_active,
            "created_on": enrollment.created.isoformat(),
            "user": {
                "username": enrollment.user.username,
                "email": enrollment.user.email,
                "password": enrollment.user.password,
                "first_name": enrollment.user.first_name,
                "last_name": enrollment.user.last_name,
                "is_active": enrollment.user.is_active,
                "is_staff": enrollment.user.is_staff,
                "is_superuser": enrollment.user.is_superuser,
                "date_joined": enrollment.user.date_joined.isoformat(),
                "last_login": enrollment.user.last_login.isoformat(),
            },
        }
        json_data = json.dumps(data)
        pprint(data)

        signature = hmac.new(
            joanie_hooks["secret"].encode("utf-8"),
            msg=json_data.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        try:
            response = requests.post(
                enrollments_hook,
                json=data,
                headers={"Authorization": "SIG-HMAC-SHA256 {:s}".format(signature)},
                verify=joanie_hooks.get("verify", True),
                timeout=1
            )
        except requests.exceptions.ReadTimeout:
            logger.error(
                "Call to enrollment hook timed out for {:s}".format(enrollment_id),
                extra={"sent": data},
            )
            self.stdout.write("Error")
            return None

        if response.status_code != requests.codes.ok:
            pprint(response.content)
            logger.error(
                "Call to enrollment hook failed for {:s}".format(enrollment_id),
                extra={"sent": data, "response": response.content},
            )
            self.stdout.write("Error")
        else:
            self.stdout.write("Success")
        return None

    def handle(self, *args, **options):
        course_ids = CourseOverview.objects.all().order_by('created').values_list('id', flat=True)
        print(course_ids)
        course_keys = [CourseKey.from_string(course_id) for course_id in course_ids]
        enrollments = CourseEnrollment.objects.filter(
            is_active=True, course_id__in=course_keys
        ).order_by('created')
        # pprint(enrollments)
        for enrollment in enrollments:
            self.update_enrollment(enrollment)
