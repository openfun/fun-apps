# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase

from courses.models import Course
from courses.choices import COURSE_LANGUAGES
from courses.utils import get_courses_per_language

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class CourseListTest(TestCase):

    def test_course_list_page_loads(self):
        url = reverse('fun-courses:index')
        response = self.client.get(url)
        self.assertContains(response, 'courses')

    def test_filter_url(self):
        url = reverse('fun-courses:filter', kwargs={'subject': 'physics'})
        self.assertEqual("/cours/#filter/subject/physics", url)


@skipUnlessLms
class CourseLanguagesTest(TestCase):
    def setUp(self):
        Course.objects.create(key='1', language='fr', is_active=True)
        Course.objects.create(key='2', language='en', is_active=True)
        Course.objects.create(key='3', language='', is_active=True)  # this should no happen but do
        Course.objects.create(key='4', language='cn', is_active=True)  # this language is not present in courses.choices.COURSE_LANGUAGES

    def test_course_list_page_loads(self):
        """Ensure /cours view do not crash when bad data is present in bdd."""
        url = reverse('fun-courses:index')
        response = self.client.get(url)
        self.assertContains(response, 'courses')

    def test_available_langues(self):
        """Ensure only available languages are returned by get_courses_per_language()."""
        languages = get_courses_per_language()
        self.assertEqual(len(COURSE_LANGUAGES), len(languages))
        self.assertEqual(
            set([c[0] for c in COURSE_LANGUAGES]),
            set([c['language'] for c in languages])
            )

    def test_get_available_langues_structure(self):
        """Ensure get_courses_per_language() returns correct dict structure."""
        languages = get_courses_per_language()
        self.assertEqual(languages[0]['language'], COURSE_LANGUAGES[0][0])
        self.assertEqual(languages[0]['count'], 1)
        self.assertEqual(languages[1]['language'], COURSE_LANGUAGES[1][0])
        self.assertEqual(languages[1]['count'], 1)
