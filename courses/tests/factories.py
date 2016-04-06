# -*- coding: utf-8 -*-

import factory

from .. import models


class CourseSubjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.CourseSubject

class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Course
    key = factory.Sequence('test/course-{0}'.format)
    is_active = True

class CourseUniversityRelationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.CourseUniversityRelation
