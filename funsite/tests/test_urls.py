from django.core.urlresolvers import reverse, resolve
from django.test import TestCase
from django.views.generic.simple import direct_to_template

from fun.tests.utils import skipUnlessLms

@skipUnlessLms        
class TestStaticUrl(TestCase):
    def test_static_url(self):
        url_reversed = reverse('tos')
        self.assertEqual(url_reversed, '/tos')
        view = resolve(url_reversed)
        self.assertEqual(view.func, direct_to_template)
