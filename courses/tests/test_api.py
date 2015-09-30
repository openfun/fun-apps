# -*- coding: utf-8 -*-

import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class CourseAPITest(TestCase):

    def setUp(self):
        self.api_url = reverse('fun-courses-api-list')

    def test_list(self):
        response = self.client.get(self.api_url)
        data = json.loads(response.content)
        self.assertIn('results', data)

