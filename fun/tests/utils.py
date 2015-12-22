# -*- coding: utf-8 -*-

import mock
import unittest
import xmltodict

from bs4 import BeautifulSoup

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

import fun.utils


def skipUnlessCms(func):
    return unittest.skipUnless(fun.utils.is_cms_running(), 'Test only valid in cms')(func)

def skipUnlessLms(func):
    return unittest.skipUnless(fun.utils.is_lms_running(), 'Test only valid in lms')(func)


class RSSDeclarationMixin():
    """This mixin is used by both Courses and News RSS feed.
    TestCase has to be carefully set up because feeds are reversely sorted.
    """
    def get_parsed_feed(self):
        response = self.client.get(self.url)
        return xmltodict.parse(response.content)['rss']

    def test_HTML_HEAD_declaration(self):
        """Test if self.url is well declared in HTML header as RSS feed."""
        url = reverse('root')
        response = self.client.get(url)
        soup = BeautifulSoup(response.content)
        declarations = soup.select('head > link[type="application/rss+xml"]')  # get all rss declarations
        self.assertTrue(any([declaration.attrs['href'] == self.url for declaration in declarations]))

    def test_feed(self):
        """Test view return status code 200."""
        self.assertEqual(200, self.client.get(self.url).status_code)

    def test_feed_for_unpublished_item(self):
        """Test item1 which should not be public is not in feed."""
        feed = self.get_parsed_feed()
        self.assertTrue('item1' not in [i['title'] for i in feed['channel']['item']])

    def test_feed_description_structure(self):
        """Test HTML description structure, see feed.html templates which chould have common structures for item title."""
        feed = self.get_parsed_feed()
        description = dict(dict(dict(feed)['channel'])['item'][0])['description']  # get the HTML description of the first item
        soup = BeautifulSoup(description)
        self.assertEqual(self.item2.title, soup.select('html h1 a')[0].text)


### Microsite test settings

def fake_microsite_get_value(name, default=None):
    """
    Create a fake microsite site name.
    """
    return settings.FAKE_MICROSITE.get(name, default)

def setMicrositeTestSettings(microsite_settings=None):
    """Decorator used to run test with microsite configuration.

    We patch microsite.get_value function, used to get the microsite configuration from the current thread.
    We patch the setting USE_MICROSITES, which activates the microsite functionality.
    """
    def wrapper(test_func):

        fake_settings = microsite_settings or settings.FAKE_MICROSITE

        test_func = mock.patch("microsite_configuration.microsite.get_value", fake_settings.get)(test_func)
        return mock.patch.dict(settings.FEATURES, {'USE_MICROSITES' : True, 'USE_CUSTOM_THEME' : False})(test_func)
    return wrapper


