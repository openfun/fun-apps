# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class CourseAPITest(TestCase):

    def setUp(self):
        self.api_url = reverse('fun-courses-api-list')

    def test_list(self):
        response = self.client.get(self.api_url)
        self.assertContains(response, 'results')

