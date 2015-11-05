# -*- coding: utf-8 -*-

from collections import OrderedDict
import datetime
import xmltodict

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase


class FeedTest(ModuleStoreTestCase):
    def setUp(self):
        super(FeedTest, self).setUp()
        self.url = reverse('fun-courses-feed')

    def get_parsed_feed(self):
        response = self.client.get(self.url)
        return xmltodict.parse(response.content)['rss']

    def test_feed(self):
        self.assertEqual(200, self.client.get(self.url).status_code)

    def test_feed_with_unpublished_course(self):
        CourseFactory(org='fun', number='001', display_name=u"unpublished", ispublic=False)
        CourseFactory(org='fun', number='002', display_name=u"published", ispublic=True)

        feed = self.get_parsed_feed()

        self.assertEqual(_(u"Fun latest published courses"), feed['channel']['title'])
        self.assertTrue(isinstance(feed['channel']['item'], OrderedDict))
        self.assertEqual(u"published", feed['channel']['item']['title'])

    def test_feed_is_sorted(self):
        now = datetime.datetime.now()
        for delta in range(30):
            start = now + datetime.timedelta(days=delta)
            CourseFactory(display_name=str(delta), start=start, ispublic=True)

        feed = self.get_parsed_feed()

        # The feed should contain only the 16 most recent courses.
        self.assertEqual(16, len(feed['channel']['item']))
        for count, delta in enumerate(range(29, 14, -1)):
            self.assertEqual(str(delta), feed['channel']['item'][count]['title'])
