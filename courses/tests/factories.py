# -*- coding: utf-8 -*-

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
    is_active = True

    class Meta(object):
        model = models.Course


class CourseUniversityRelationFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.CourseUniversityRelation
