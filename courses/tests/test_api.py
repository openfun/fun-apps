# -*- coding: utf-8 -*-

import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now, timedelta

from fun.tests.utils import skipUnlessLms

from universities.factories import UniversityFactory

from .factories import CourseFactory, CourseSubjectFactory
from courses import choices as courses_choices
from courses.models import CourseUniversityRelation


@skipUnlessLms
class CourseAPITest(TestCase):

    def setUp(self):
        self.api_url = reverse('fun-courses-api-list')
        self.active_1 = CourseFactory(title='active course 1',
            show_in_catalog=True,
            is_active=True,
        )
        self.active_2 = CourseFactory(title='active course 2',
            show_in_catalog=True,
            is_active=True,
        )
        self.not_active = CourseFactory(
            title='course not active',
            show_in_catalog=True,
            is_active=False,
        )
        self.not_in_catalog = CourseFactory(
            title='course not in catalog',
            show_in_catalog=False,
            is_active=True,
        )

    @property
    def soon(self):
        return now() + timedelta(days=1)

    @property
    def too_late(self):
        return now() + timedelta(days=1000)

    def test_course_list_api_response_loads(self):
        response = self.client.get(self.api_url)
        data = json.loads(response.content)
        self.assertIn('results', data)

    def test_response_contains_on_active_courses(self):
        response = self.client.get(self.api_url)
        self.assertContains(response, self.active_1.title)
        self.assertContains(response, self.active_2.title)
        self.assertNotContains(response, self.not_active.title)
        self.assertNotContains(response, self.not_in_catalog.title)

    def test_only_display_courses_for_a_specific_university(self):
        university = UniversityFactory(code='test-university')
        UniversityFactory(code='another-university')
        CourseUniversityRelation.objects.create(
            course=self.active_1, university=university
        )
        filter_data = {'university': 'test-university'}
        response = self.client.get(self.api_url, filter_data)
        self.assertContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)
        filter_data = {'university': 'another-university'}
        response = self.client.get(self.api_url, filter_data)
        self.assertNotContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)

    def test_only_display_courses_for_a_specific_subject(self):
        subject = CourseSubjectFactory(slug='test-subject')
        UniversityFactory(slug='another-subject')
        self.active_1.subjects.add(subject)
        filter_data = {'subject': 'test-subject'}
        response = self.client.get(self.api_url, filter_data)
        self.assertContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)
        filter_data = {'subject': 'another-subject'}
        response = self.client.get(self.api_url, filter_data)
        self.assertNotContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)

    def test_only_display_courses_for_a_specific_level(self):
        self.active_1.level = courses_choices.COURSE_LEVEL_INTRODUCTORY
        self.active_1.save()
        filter_data = {'level': courses_choices.COURSE_LEVEL_INTRODUCTORY}
        response = self.client.get(self.api_url, filter_data)
        self.assertContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)
        filter_data = {'level': courses_choices.COURSE_LEVEL_ADVANCED}
        response = self.client.get(self.api_url, filter_data)
        self.assertNotContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)

    def test_only_display_courses_starting_soon(self):
        self.active_1.start_date = self.soon
        self.active_1.save()
        self.active_2.start_date = self.too_late
        self.active_2.save()
        filter_data = {'availability': 'start-soon'}
        response = self.client.get(self.api_url, filter_data)
        self.assertContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)

    def test_only_display_courses_ending_soon(self):
        self.active_1.end_date = self.soon
        self.active_1.save()
        self.active_2.end_date = self.too_late
        self.active_2.save()
        filter_data = {'availability': 'end-soon'}
        response = self.client.get(self.api_url, filter_data)
        self.assertContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)

    def test_only_display_new_courses(self):
        self.active_1.session_number = 1
        self.active_1.save()
        self.active_2.session_number = 2
        self.active_2.save()
        filter_data = {'availability': 'new'}
        response = self.client.get(self.api_url, filter_data)
        self.assertContains(response, self.active_1.title)
        self.assertNotContains(response, self.active_2.title)
