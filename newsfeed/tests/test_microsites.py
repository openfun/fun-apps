# -*- coding: utf-8 -*-

import datetime

from bs4 import BeautifulSoup

from django.core.urlresolvers import reverse

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from backoffice.tests.test_microsites import FAKE_MICROSITE1, FAKE_MICROSITE2
from fun.tests.utils import skipUnlessLms, setMicrositeTestSettings

from ..models import Article


@skipUnlessLms
class TestNews(ModuleStoreTestCase):
    def setUp(self):
        Article.objects.create(title=u"Microsite 1", slug='microsite1',
                microsite='microsite1', published=True, created_at=datetime.datetime.now())
        Article.objects.create(title=u"Microsite 2", slug='microsite2',
                microsite='microsite2', published=True, created_at=datetime.datetime.now())
        UserFactory.create(username='admin', password='password', is_superuser=True, is_staff=True)

    @setMicrositeTestSettings(FAKE_MICROSITE1)
    def test_microsite1(self):
        response = self.client.get(reverse('newsfeed-landing'))
        soup = BeautifulSoup(response.content)
        left_articles = soup.find(class_='fun-news').find_all(class_='left')
        right_articles = soup.find(class_='fun-news').find_all(class_='right')
        self.assertEqual(1, len(left_articles))
        self.assertEqual(0, len(right_articles))
        self.assertIn(u"Microsite 1", left_articles[0].find("h3").text)


    @setMicrositeTestSettings(FAKE_MICROSITE1)
    def test_featured_article_is_not_displayed(self):
        # TODO: because FeaturedSection is a singleton, featured articles will
        # be displayed on every microsite. This should be fixed.
        pass
