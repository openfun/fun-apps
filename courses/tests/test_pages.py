# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase



class CourseListTest(TestCase):

    def test_course_list_page_loads(self):
        url = reverse('fun-courses-index')
        response = self.client.get(url)
        self.assertContains(response, 'courses')
