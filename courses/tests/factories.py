# -*- coding: utf-8 -*-

import factory

from .. import models


class CourseSubjectFactory(factory.DjangoModelFactory):
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
