# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class BaseTestCase(ModuleStoreTestCase):
    def setUp(self):
        self.course = CourseFactory.create(org='org')

    def test_free_course(self):
        response = self.client.get(reverse('about_course', args=[self.course.key]))
        self.assertEqual(200, response.status_code)