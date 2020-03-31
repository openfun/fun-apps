# -*- coding: utf-8 -*-

from datetime import date, timedelta
import logging
from smtplib import SMTPRecipientsRefused

from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.contrib.auth import models as auth_models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

from student.models import CourseEnrollment
from opaque_keys.edx.keys import CourseKey

from courses.models import Course

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """This command change users's enrollment mode from audit to honor"""
    # Since Eucalyptus, edx-platform does not allow default enrollment mode
    # `audit` to get web certificate.
    # This script will be run periodically to change all new enrollment modes
    # from `audit` to `honor`, then emails a report.
    # https://fun.plan.io/issues/4001

    def handle(self, *args, **options):

        changed = CourseEnrollment.objects.filter(mode='audit').update(mode='honor')

        subject = "[%s] CRONJOB: Change audit enrollments to honor" % settings.PLATFORM_NAME

        text_content = (
            "CRONJOB: Update course `audit` enrollments to `honor`.\n"
            "%d CourseEnrollment objects updated."
        ) % changed

        email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=settings.ADMINS,
            )
        try:
            email.send()
        except SMTPRecipientsRefused as e:
            logger.error(u"Stat email could not be sent(%s): %s.", subject, e.message)
