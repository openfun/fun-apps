# -*- coding: utf-8 -*-

import xmltodict

from django.core.urlresolvers import reverse

from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase


class FeedTest(ModuleStoreTestCase):
    def setUp(self):
        super(FeedTest, self).setUp()
        self.unpublished_course = CourseFactory(org='fun', number='001', display_name=u"unpublished", ispublic=False)
        self.published_course = CourseFactory(org='fun', number='002', display_name=u"published", ispublic=True)
        self.url = reverse('fun-courses-feed')

    def test_feed(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        data = xmltodict.parse(response.content)
        self.assertEqual(u"Fun latest published courses", data['rss']['channel']['title'])
        self.assertEqual(1, len(data['rss']['channel']['item']))
        self.assertEqual(u"published", data['rss']['channel']['item'][0]['title'])
