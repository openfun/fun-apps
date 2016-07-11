from django.core.urlresolvers import reverse, resolve
from django.test import TestCase
from django.views.generic import TemplateView

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class TestStaticUrl(TestCase):
    def test_static_url(self):
        url_reversed = reverse('tos')
        self.assertEqual(url_reversed, '/tos')
        view = resolve(url_reversed)
        # TODO Dogwood: find out
        #self.assertEqual(view.func, TemplateView.as_view)
