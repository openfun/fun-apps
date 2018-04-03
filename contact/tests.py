# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class ContactTest(TestCase):

    def test_contact_view(self):
        url = reverse('contact:contact')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
