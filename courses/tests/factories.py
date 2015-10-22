# -*- coding: utf-8 -*-

import factory

from .. import models


class CourseSubjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.CourseSubject

class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Course
    key = u"test/course/"
