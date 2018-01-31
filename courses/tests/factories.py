# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz
from random import randint, randrange

from django.utils import timezone

import factory
from factory import fuzzy

from .. import models


class CourseSubjectFactory(factory.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=255)
    short_name = fuzzy.FuzzyText(length=100)
    slug = factory.Sequence("subject {0}".format)
    description = fuzzy.FuzzyText(length=1000)
    featured = factory.fuzzy.FuzzyChoice((True, False))
    image = factory.django.ImageField(color='white')
    score = factory.fuzzy.FuzzyInteger(low=0, high=999)

    class Meta(object):
        model = models.CourseSubject


class CourseFactory(factory.DjangoModelFactory):

    key = factory.Sequence('test/course-{0}'.format)
    show_in_catalog = fuzzy.FuzzyChoice((True, False))

    is_active = True

    class Meta(object):
        model = models.Course

    @factory.lazy_attribute
    def start_date(self):
        """
        A start date for the course is chosen randomly in the future (it can
        also be forced), then the other significant dates for the course are
        chosen randomly in periods that make sense with this start date.
        """
        now = timezone.now()
        period = timedelta(days=1000)
        return pytz.timezone('UTC').localize(datetime.fromordinal(randrange(
            now.toordinal(), (now + period).toordinal())))

    @factory.lazy_attribute
    def end_date(self):
        """
        The end date is at a random duration after the start date.
        """
        if not self.start_date:
            return None
        period = timedelta(days=90)
        return pytz.timezone('UTC').localize(datetime.fromordinal(randrange(
            self.start_date.toordinal(), (self.start_date + period).toordinal())))

    @factory.lazy_attribute
    def enrollment_start_date(self):
        """
        The start of enrollment date is a random date before the start date.
        """
        if not self.start_date:
            return None
        period = timedelta(days=90)
        return pytz.timezone('UTC').localize(datetime.fromordinal(randrange(
            (self.start_date - period).toordinal(), self.start_date.toordinal())))

    @factory.lazy_attribute
    def enrollment_end_date(self):
        """
        The end of enrollment date is a random date between the start of enrollment date
        and the end of course date.

        If the enrollment start date and end date have been forced to incoherent dates,
        then just don't set any end of enrollment date...
        """
        if not self.start_date:
            return None
        end_date = self.end_date or self.start_date + timedelta(days=randint(1, 90))
        if end_date < self.enrollment_start_date:
            return None
        return pytz.timezone('UTC').localize(datetime.fromordinal(randrange(
            self.enrollment_start_date.toordinal(), end_date.toordinal())))


class CourseUniversityRelationFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.CourseUniversityRelation
