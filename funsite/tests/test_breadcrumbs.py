# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from fun.tests.utils import skipUnlessLms

from ..utils import breadcrumbs


@skipUnlessLms
class TestBreadcrumbs(TestCase):

    def test_static_pages(self):
        url = '/privacy'
        breadcrumbs_list = breadcrumbs(url, u"Privacy")
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), ('#', u"Privacy")],)

        url = '/contact'
        breadcrumbs_list = breadcrumbs(url, u"Contact")
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), ('#', u"Contact")],)

    def test_course_list(self):
        url = '/cours/'
        breadcrumbs_list = breadcrumbs(url, _("Courses"))
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), ('#', _("Courses"))],)

    def test_course_about_page(self):
        url = '/courses/fun/001/now/about'
        breadcrumbs_list = breadcrumbs(url, u"Test course")
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), (reverse('fun-courses:index'), _("All courses")), ('#', u"Test course")],)

    def test_news_detail_page(self):
        url = '/news/test-news'
        breadcrumbs_list = breadcrumbs(url, u"Test news")
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), (reverse('newsfeed-landing'), _("News")), ('#', u"Test news")],)

    def test_university_page(self):
        url = '/universities/fun-paris-V'
        breadcrumbs_list = breadcrumbs(url, u"FUN Paris V")
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), (reverse('universities-landing'), _(u"Universities")), ('#', u"FUN Paris V")],)

    def test_login_page(self):
        # login page exists at /login and /accounts/login yeah !
        url = '/login'
        breadcrumbs_list = breadcrumbs(url, u"Login")
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), ('#', u"Login")],)

        url = '/accounts/login'
        breadcrumbs_list = breadcrumbs(url, u"Accounts/Login")
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), ('#', u"Accounts/Login")],)
