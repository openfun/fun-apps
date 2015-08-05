# -*- coding: utf-8 -*-

import factory

from .. import models


class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Course
    key = u"test/course/"
