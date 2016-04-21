# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext as _

from course_modes.models import CourseMode
from opaque_keys.edx.keys import CourseKey

from fun.tests.utils import skipUnlessLms

from ..utils import breadcrumbs, is_paid_course


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

    def test_terms_page(self):
        url = reverse('payment:terms-page')
        breadcrumbs_list = breadcrumbs(url, _("Verified exam terms and conditions"))
        self.assertEqual(breadcrumbs_list,
                [('/', _("Home")), ('#', _("Verified exam terms and conditions"))],)

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


@skipUnlessLms
class TestCourseModes(TestCase):
    def setUp(self):
        self.coursekey1 = CourseKey.from_string('course1/fun/session1')
        self.coursekey2 = CourseKey.from_string('course2/fun/session1')
        CourseMode.objects.create(course_id=self.coursekey1, mode_slug='verified', min_price=100)
        CourseMode.objects.create(course_id=self.coursekey2, mode_slug='honor', min_price=0)
        CourseMode.objects.create(course_id=self.coursekey2, mode_slug='verified', min_price=100)

    def test_is_paid_course(self):
        course_modes = is_paid_course(str(self.coursekey1))
        self.assertEqual(100, course_modes['verified'])

        course_modes = is_paid_course(str(self.coursekey2))
        self.assertEqual(100, course_modes['verified'])
        self.assertEqual(0, course_modes['honor'])

        course_modes = is_paid_course('dummy/key/fun')
        self.assertEqual({}, course_modes)
