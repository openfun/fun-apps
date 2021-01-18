# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.core.management import call_command

from celery import shared_task
from microsite_configuration import microsite
from opaque_keys.edx.keys import CourseKey
import requests
from xmodule.modulestore.django import modulestore

logger = logging.getLogger(__name__)


@shared_task
def update_courses_meta_data(*args, **kwargs):
    """
    A task to call when a course is updated in OpenEdX.
    It calls:
    - the "update_courses" management command to update the "fun-apps" search index.
    - each course run hook url defined in the `COURSE_HOOKS` setting with scheduling information
    """
    # Update fun-apps course catalog
    call_command("update_courses", *args, **kwargs)

    hooks = getattr(settings, "COURSE_HOOKS", [])
    if not hooks:
        return

    # Synchronize with external course hook
    course_id = kwargs["course_id"]
    course_key = CourseKey.from_string(course_id)
    course = modulestore().get_course(course_key)
    edxapp_domain = microsite.get_value("site_domain", settings.LMS_BASE)
    data = {
        "resource_link": "https://{:s}/courses/{:s}/info".format(
            edxapp_domain, course_id
        ),
        "start": course.start and course.start.isoformat(),
        "end": course.end and course.end.isoformat(),
        "enrollment_start": course.enrollment_start and course.enrollment_start.isoformat(),
        "enrollment_end": course.enrollment_end and course.enrollment_end.isoformat(),
        "languages": ["fr"],
    }
    json_data = json.dumps(data)

    for hook in hooks:
        signature = hmac.new(
            hook["secret"].encode("utf-8"),
            msg=json_data.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        response = requests.post(
            hook["url"],
            json=data,
            headers={"Authorization": "SIG-HMAC-SHA256 {:s}".format(signature)},
            verify=hook.get("verify", True),
        )

        if response.status_code != requests.codes.ok:
            logger.error(
                "Call to course hook failed for {:s}".format(course_id),
                extra={"sent": data, "response": response.content},
            )
