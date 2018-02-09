# -*- coding: utf-8 -*-
import random

from django.db import connection, models
from django.db.models import Q
from django.utils.timezone import now, timedelta

from . import settings as courses_settings


def annotate_with_public_courses(queryset):
    """
    Annotate a queryset with a "public_courses_count" attribute.

    queryset: refer to a model with a `courses` attribute.
    """
    return queryset.filter(
        courses__is_active=True,
        courses__show_in_catalog=True
    ).annotate(public_courses_count=models.Count('courses'))


class CourseSubjectManager(models.Manager):

    def by_score(self):
        return self.order_by('-score', 'name')

    def featured(self):
        return self.filter(featured=True).exclude(image='')

    def random_featured(self):
        return self.featured().order_by('?')


class CourseQuerySet(models.query.QuerySet):

    @property
    def too_late(self):
        return now() + timedelta(days=courses_settings.NUMBER_DAYS_TOO_LATE)

    def too_late_range(self):
        return (now(), self.too_late)

    def with_related(self):
        queryset = self.prefetch_related(
            'subjects', 'universities',
            'related_universities',
        )
        return queryset

    def public(self):
        return self.filter(is_active=True, show_in_catalog=True)

    def starting_soon(self):
        return self.public().filter(start_date__gt=now())

    def ending_soon(self):
        return self.public().filter(end_date__range=self.too_late_range())

    def enrollment_ends_soon(self):
        return self.public().filter(enrollment_end_date__range=self.too_late_range())

    def new(self):
        """
        A new course is in its first session and for which enrollment is not closed.
        """
        return self.public().filter(
            Q(session_number=1),
            Q(enrollment_end_date__gte=now()) | Q(enrollment_end_date__isnull=True))

    def opened(self):
        """
        A course that is currently opened for enrollment.
        """
        return self.public().filter(
            Q(enrollment_start_date__lte=now()) | Q(enrollment_start_date__isnull=True),
            Q(enrollment_end_date__gte=now()) | Q(enrollment_end_date__isnull=True))

    def started(self):
        """
        A course that is on-going.
        """
        return self.public().filter(
            Q(start_date__lte=now()) | Q(start_date__isnull=True),
            Q(end_date__gte=now()) | Q(end_date__isnull=True))

    def archived(self):
        """
        A course is archived if it has an end date in the past.
        """
        return self.public().filter(end_date__lt=now(), end_date__isnull=False)

    def annotate_for_ordering(self):
        """
        Add attributes to all results for ordering purposes:
          1) has_ended: course that have ended will always be at the end,
          2) is_enrollment_over: courses for which enrollment is over will come
             after the ones that are still open,
          3) has_started: courses that have started will always be presented
             before courses that have yet to start,
          4) ordering_date: Lastly, if the course is started we will use its end
             of enrollment date to rank it, otherwise we will use its start date.
        """
        # We are putting raw sql in the extra(...) statement. To do that,
        # we need the proper datetime formatting, which varies for every db.
        formatted_now = connection.ops.value_to_db_datetime(now())

        return self.extra(select={
            'has_ended': '(end_date IS NOT NULL AND end_date < "{now}")'.format(now=formatted_now),

            'is_enrollment_over': (
                '(enrollment_end_date IS NOT NULL AND enrollment_end_date < "{now}")'
            ).format(now=formatted_now),

            'has_started': '(start_date < "{now}" OR start_date IS NULL)'.format(now=formatted_now),

            'ordering_date': (
                'CASE WHEN start_date < "{now}" OR start_date IS NULL '
                'THEN enrollment_end_date ELSE start_date END'
            ).format(now=formatted_now)})

    def by_score(self):
        return self.public().order_by('-score')

    def random_featured(self, limit_to=7):
        courses = self.by_score().prefetch_related("related_universities__university")[:limit_to]
        courses = list(courses)
        random.shuffle(courses)
        return courses
