# -*- coding: utf-8 -*-
import random

from django.db import models
from django.utils.timezone import now, timedelta

from fun.utils.managers import ChainableManager

from . import settings as courses_settings


class CourseSubjectManager(models.Manager):

    def with_related(self):
        queryset = self.prefetch_related('courses')
        queryset = queryset.annotate(courses_count=models.Count('courses'))
        return queryset

    def by_score(self):
        return self.with_related().order_by('-score')

    def by_name(self):
        return self.with_related().order_by('name')

    def featured(self):
        return self.filter(featured=True, image__isnull=False)

    def random_featured(self):
        return self.featured().order_by('?')


class CourseQuerySet(models.query.QuerySet):

    @property
    def too_late(self):
        return now() + timedelta(days=courses_settings.NUMBER_DAYS_TOO_LATE)

    def with_related(self):
        queryset = self.prefetch_related('subjects', 'universities')
        return queryset

    def active(self):
        return self.filter(is_active=True)

    def start_soon(self):
        return self.active().filter(start_date__range=(now(), self.too_late))

    def end_soon(self):
        return self.active().filter(end_date__range=(now(), self.too_late))

    def by_score(self):
        return self.active().order_by('-score')


class CourseManager(ChainableManager):
    queryset_class = CourseQuerySet

    def random_featured(self, limit_to=7):
        courses = self.by_score()[:limit_to]
        courses = list(courses)
        random.shuffle(courses)
        return courses
