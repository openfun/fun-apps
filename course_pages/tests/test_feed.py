# -*- coding: utf-8 -*-

import datetime
import xmltodict

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from fun.tests.utils import skipUnlessLms
from courses.models import Course, CourseUniversityRelation
from universities.factories import UniversityFactory


@skipUnlessLms
class FeedTest(ModuleStoreTestCase):
    def setUp(self):
        super(FeedTest, self).setUp()
        date = datetime.datetime(2015, 1, 1)

        self.url = reverse('fun-courses:feed')
        CourseFactory(org='fun', course='course1', name='course1', display_name=u"unpublished", ispublic=False)
        CourseFactory(org='fun', course='course2', name='course2', display_name=u"published", ispublic=True,
                start=date,
                end=date + datetime.timedelta(days=15))
        CourseFactory(org='fun', course='course3', name='course3', display_name=u"published", ispublic=True,
                start=date + datetime.timedelta(days=30),
                end=date + datetime.timedelta(days=60))

        university1 = UniversityFactory(name=u"Université Paris Descartes")
        university2 = UniversityFactory(name=u"FÛN")
        self.course1 = Course.objects.get(key='fun/course1/course1')
        self.course2 = Course.objects.get(key='fun/course2/course2')
        self.course3 = Course.objects.get(key='fun/course3/course3')
        CourseUniversityRelation.objects.create(university=university1, course=self.course2)
        CourseUniversityRelation.objects.create(university=university2, course=self.course3)
        CourseUniversityRelation.objects.create(university=university1, course=self.course3)

    def get_parsed_feed(self):
        response = self.client.get(self.url)
        return xmltodict.parse(response.content)['rss']

    def test_feed(self):
        self.assertEqual(200, self.client.get(self.url).status_code)

    def test_feed_for_unpublished_course(self):
        feed = self.get_parsed_feed()
        self.assertTrue('course1' not in [i['title'] for i in feed['channel']['item']])

    def test_feed_structure(self):
        feed = self.get_parsed_feed()
        self.assertEqual(_(u"Fun latest published courses"), feed['channel']['title'])
        course2 = dict(feed['channel']['item'][0])  # course2 should be first
        course3 = dict(feed['channel']['item'][1])
        self.assertEqual('course2', course2['title'])
        self.assertEqual('course3', course3['title'])
        self.assertEqual(u'2015-01-01T00:00:00+00:00', course2['start_date'])
        self.assertEqual(u'2015-01-31T00:00:00+00:00', course3['start_date'])
        self.assertEqual(u"Université Paris Descartes", course2['university'])
        self.assertEqual(u"FÛN", course3['university'])
