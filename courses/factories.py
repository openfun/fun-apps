# -*- coding: utf-8 -*-

import factory

from xmodule.modulestore.tests.factories import CourseFactory

from .models import Course


class CourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Course


class FunCourseFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Course

        UniversityFactory(name=u"University1", code='univ1')
        UniversityFactory(name=u"University2", code='univ2')
        CourseFactory(org='univ1', number='001', display_name=u"Course1", ispublic=True)
        CourseFactory(org='univ2', number='002', display_name=u"Course2", ispublic=True)
