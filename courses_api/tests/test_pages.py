# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class CourseListTest(TestCase):

    def test_course_list_page_loads(self):
        url = reverse('fun-courses:index')
        response = self.client.get(url)
        self.assertContains(response, 'courses')

    def test_filter_url(self):
        url = reverse('fun-courses:filter', kwargs={'subject': 'physics'})
        self.assertEqual("/cours/#filter/subject/physics", url)
