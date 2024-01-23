# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
import time
from pprint import pprint

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from microsite_configuration import microsite

from student.models import CourseEnrollment


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update FUN's course data."

    def update_enrollment(self, enrollments, batch):
        joanie_hooks = getattr(settings, "JOANIE_HOOKS")
        if not joanie_hooks:
            return

        enrollments_hook = joanie_hooks.get('hooks', {}).get('enrollments')
        if not enrollments_hook:
            return

        edxapp_domain = microsite.get_value("site_domain", settings.LMS_BASE)

        self.stdout.write('Preparing data… ', ending='')
        start_time = time.time()
        data = {
            "enrollments": [
                {
                    "resource_link": "https://{:s}/courses/{:s}/course".format(
                        edxapp_domain, enrollment.get("course_id")
                    ),
                    "is_active": enrollment.get("is_active"),
                    "created_on": enrollment.get("created").isoformat(),
                    "username": enrollment.get("user__username"),
                }
                for enrollment in enrollments
            ]
        }
        data_time = time.time()
        self.stdout.write('{:.2f} | '.format(data_time - start_time), ending='')

        json_data = json.dumps(data)
        self.stdout.write('Sending… ', ending='')

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
                timeout=5
            )
            end_time = time.time()
        except requests.exceptions.ReadTimeout:
            logger.error(
                "Call to enrollment hook timed out for batch {}/{}".format(*batch),
                # extra={"sent": data},
            )
            end_time = time.time()
            self.stdout.write('{:.2f} | '.format(end_time - data_time), ending='')
            self.stdout.write("Error", ending='')
            return None
        self.stdout.write('{:.2f} | '.format(end_time - data_time), ending='')

        if response.status_code != requests.codes.ok:
            pprint(response.content)
            logger.error(
                "Call to enrollment hook failed for batch {}/{}".format(*batch),
                extra={"response": response.content},
            )
            self.stdout.write("Error", ending='')
        else:
            self.stdout.write("Success", ending='')
        del data
        return None

    def handle(self, *args, **options):
        enrollments_batch_size = 1000
        enrollments_count = CourseEnrollment.objects.all().count()
        for current_enrollment_index in range(0, enrollments_count, enrollments_batch_size):
            start_time = time.time()
            enrollments = CourseEnrollment.objects.all().values(
                'course_id', 'is_active', 'created', 'user__username'
            )[
                current_enrollment_index:current_enrollment_index + enrollments_batch_size
            ].iterator()
            request_time = time.time()
            self.stdout.write(
                'Enrollment {}-{}/{} {:.5f} | '.format(
                    current_enrollment_index,
                    current_enrollment_index + enrollments_batch_size,
                    enrollments_count,
                    request_time - start_time,
                ),
                ending=''
            )
            self.update_enrollment(
                enrollments,
                batch=(
                    current_enrollment_index,
                    current_enrollment_index + enrollments_batch_size
                )
            )
            end_time = time.time()
            self.stdout.write(' {:.2f}'.format(end_time - start_time))

        print("Done !!!")
