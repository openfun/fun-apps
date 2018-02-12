# -*- coding: utf-8 -*-

import datetime
import pytz

from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils.translation import ugettext_lazy as _

from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from courses.tests.factories import CourseFactory as FunCourseFactory
from fun.tests.utils import skipUnlessLms, RSSDeclarationMixin
from courses.models import CourseUniversityRelation
from universities.tests.factories import UniversityFactory


@skipUnlessLms
class FeedTest(ModuleStoreTestCase, RSSDeclarationMixin):
    def setUp(self):
        super(FeedTest, self).setUp()
        date = datetime.datetime(2015, 1, 1, 0, 0, 0, tzinfo=pytz.utc)

        self.url = reverse('fun-courses:feed')
        CourseFactory(org='fun', course='course1', name='item1', display_name=u"unpublished", ispublic=False)
        CourseFactory(org='fun', course='course2', name='item2', display_name=u"published", ispublic=True,
                start=date,
                end=date + datetime.timedelta(days=15))
        CourseFactory(org='fun', course='course3', name='item3', display_name=u"published", ispublic=True,
                start=date + datetime.timedelta(days=30),
                end=date + datetime.timedelta(days=60))

        university1 = UniversityFactory(name=u"Université Paris Descartes")
        university2 = UniversityFactory(name=u"FÛN")
        self.item1 = FunCourseFactory(key='fun/course1/item1', title='item1', show_in_catalog=False)
        self.item2 = FunCourseFactory(key='fun/course2/item2', title='item2',
                start_date=date, end_date=date + datetime.timedelta(days=15))
        self.item3 = FunCourseFactory(key='fun/course3/item3', title='item3',
                start_date=date + datetime.timedelta(days=30), end_date=date + datetime.timedelta(days=60))
        CourseUniversityRelation.objects.create(university=university1, course=self.item2)
        CourseUniversityRelation.objects.create(university=university2, course=self.item3)
        CourseUniversityRelation.objects.create(university=university1, course=self.item3)

    def test_feed_xml_structure(self):
        feed = self.get_parsed_feed()
        self.assertEqual(_(u"Fun latest published courses"), feed['channel']['title'])
        course2 = dict(feed['channel']['item'][0])  # course2 should be first
        course3 = dict(feed['channel']['item'][1])
        self.assertEqual('item2', course2['title'])
        self.assertEqual('item3', course3['title'])
        #TODO Dogwood: time zone issue (template rendered date is timezoned)
        #self.assertEqual(u'2015-01-01T00:00:00+00:00', course2['start_date'])
        #self.assertEqual(u'2015-01-31T00:00:00+00:00', course3['start_date'])
        self.assertEqual(u"Université Paris Descartes", course2['university'])
        self.assertEqual(u"FÛN", course3['university'])
