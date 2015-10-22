# -*- coding: utf-8 -*-
import random

from django.db import models
from django.utils.timezone import now, timedelta

from fun.utils.managers import ChainableManager

from . import settings as courses_settings


def annotate_with_public_courses(queryset):
    """Annotate a querysets with a public_courses_count attribute.

    queryset: refer to a model with a `courses` attribute.
    """
    return queryset.filter(
        courses__is_active=True,
        courses__show_in_catalog=True
    ).annotate(public_courses_count=models.Count('courses'))


class CourseSubjectManager(models.Manager):

    def by_score(self):
        return self.order_by('-score')

    def featured(self):
        return self.filter(featured=True)

    def random_featured(self):
        return self.featured().order_by('?')


class CourseQuerySet(models.query.QuerySet):

    @property
    def too_late(self):
        return now() + timedelta(days=courses_settings.NUMBER_DAYS_TOO_LATE)

    def with_related(self):
        queryset = self.prefetch_related('subjects', 'universities')
        return queryset

    def public(self):
        return self.filter(is_active=True, show_in_catalog=True)

    def start_soon(self):
        return self.public().filter(start_date__range=(now(), self.too_late))

    def end_soon(self):
        return self.public().filter(end_date__range=(now(), self.too_late))

    def by_score(self):
        return self.public().order_by('-score')


class CourseManager(ChainableManager):
    queryset_class = CourseQuerySet

    def random_featured(self, limit_to=7):
        courses = self.by_score().prefetch_related("related_universities__university")[:limit_to]
        courses = list(courses)
        random.shuffle(courses)
        return courses
