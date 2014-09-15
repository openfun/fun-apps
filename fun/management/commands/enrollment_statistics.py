# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
import logging

from django.db.models import Q, Count
from django.template.loader import render_to_string
from django.contrib.auth import models as auth_models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand, CommandError

from student.models import CourseEnrollment

logger = logging.getLogger(__name__)

DATE_FORMAT = '%A %d %B'
SHORT_DATE_FORMAT = '%d/%m/%Y'


class Command(BaseCommand):
    help = """
    """

    def handle(self, *args, **options):
        today = date.today()
        period = today - timedelta(days=7)
        context = {}
        context['all_register'] = auth_models.User.objects.filter(Q(is_superuser=False),
                Q(is_active=True)).count()
        context['new_register'] = auth_models.User.objects.filter(Q(is_superuser=False),
                Q(is_active=True)).filter(date_joined__gt=period).count()

        context['all_course_distribution'] = CourseEnrollment.objects.values('course_id'
                ).annotate(count=Count('course_id')).order_by('course_id')
        context['new_course_distribution'] = CourseEnrollment.objects.filter(created__gt=period
                ).values('course_id').annotate(count=Count('course_id')).order_by('course_id')


        context['subject'] = u"[FUN] Statistiques d'inscription pour la période du %s au %s" % (
                period.strftime(SHORT_DATE_FORMAT), today.strftime(SHORT_DATE_FORMAT))
        html_content = render_to_string('fun/emails/stats_email.html', context)
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
        except SMTPRecipientsRefused:
            logger.error(u"Stat email could not be sent(%s)." % subject)



