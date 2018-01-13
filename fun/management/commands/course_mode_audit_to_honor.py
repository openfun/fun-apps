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
    # Since Eucalyptus, edx-platform do not allow honor users to get certification and default enrollment is audit
    # This code aims to avoid this problem, to allow certification with actual code base,
    # until we upgrade to newer edX version and rethink our certificat process
    # It also emails a report of modification done by course as we want to follow course registrations
    # https://fun.plan.io/issues/4001

    def handle(self, *args, **options):
        
        context = {}
        context['report'] = []
        # select CourseEnrollment which have at least 1 audit mode
        for course_enrollment in CourseEnrollment.objects.filter(mode='audit').annotate(Count('mode', distinct=True)).order_by('course_id'):
            changed = CourseEnrollment.objects.filter(course_id=course_enrollment.course_id, mode='audit').update(mode='honor')
            context['report'].append([course_enrollment.course_id, changed])

        context['subject'] = "[%s] Change audit enrollments to honor" % settings.PLATFORM_NAME
        
#        import ipdb; ipdb.set_trace()

        html_content = render_to_string('fun/emails/course_mode_audit_to_honor.html', context)
        text_content = "This is a HTML only email"
        email = EmailMultiAlternatives(
                subject=context['subject'],
                body=text_content,
                from_email=settings.STATS_EMAIL,
                to=settings.STATS_RECIPIENTS,
            )
        email.attach_alternative(html_content, "text/html")
        try:
            email.send()
        except SMTPRecipientsRefused as e:
            logger.error(u"Stat email could not be sent(%s): %s.", context['subject'], e.message)
