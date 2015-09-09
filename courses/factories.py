# -*- coding: utf-8 -*-

import factory


from .models import Course


class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Course

