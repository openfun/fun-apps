# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from fun.tests.utils import skipUnlessLms

from .factories import CourseFactory as FunCourseFactory


@skipUnlessLms
class CourseAPITest(ModuleStoreTestCase):

    def setUp(self):
        super(CourseAPITest, self).setUp()
        self.api_url = reverse('fun-courses-api-list')
        FunCourseFactory(key='univ1/001/Course1')

    def test_list(self):
        response = self.client.get(self.api_url)
        self.assertContains(response, 'Course1')
