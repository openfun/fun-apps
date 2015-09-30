# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class CourseListTest(TestCase):
    def setUp(self):
        super(CourseListTest, self).setUp()
        self.url = reverse('fun-courses-index')

    def test_list_page_loads(self):
        response = self.client.get(self.url)
        self.assertContains(response, 'course')
