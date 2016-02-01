# -*- coding: utf-8 -*-

import datetime

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from fun.tests.utils import skipUnlessLms, RSSDeclarationMixin

from .factories import ArticleCategoryFactory, ArticleFactory


@skipUnlessLms
class TestNewsFeed(TestCase, RSSDeclarationMixin):
    def setUp(self):
        self.url = reverse('newsfeed-rss')
        category = ArticleCategoryFactory()
        date = datetime.datetime(2015, 1, 1)
        self.item1 = ArticleFactory(published=False, title=u"Title 1", category=category, created_at=date)
        self.item2 = ArticleFactory(published=True, title=u"Title 2", category=category,
                                    created_at=date + datetime.timedelta(days=15))
        self.item3 = ArticleFactory(published=True, title=u"Title 3", created_at=date)

    def test_feed_xml_structure(self):
        feed = self.get_parsed_feed()
        self.assertEqual(_(u"Fun latest published news"), feed['channel']['title'])
        item2 = dict(feed['channel']['item'][0])  # article 2 should be first
        item3 = dict(feed['channel']['item'][1])
        self.assertEqual('Title 2', item2['title'])
        self.assertEqual('Title 3', item3['title'])
