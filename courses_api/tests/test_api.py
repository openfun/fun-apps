# -*- coding: utf-8 -*-

import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now, timedelta

from student.tests.factories import UserFactory

from fun.tests.utils import skipUnlessLms
from universities.factories import UniversityFactory

from courses import choices as courses_choices
from courses.models import CourseUniversityRelation
from courses.tests.factories import CourseFactory, CourseSubjectFactory


@skipUnlessLms
class CourseAPITest(TestCase):

    def setUp(self):
        self.api_url = reverse('fun-courses-api:courses-list')
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
        self.user = UserFactory(username='user', password='password') # user with profile

    def login_as_admin(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='user', password='password')

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

    def test_response_contains_only_active_courses(self):
        response = self.client.get(self.api_url)
        self.assertContains(response, self.active_1.title)
        self.assertContains(response, self.active_2.title)
        self.assertNotContains(response, self.not_active.title)
        self.assertNotContains(response, self.not_in_catalog.title)

    def test_staff_user_can_see_courses_not_catalog(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='user', password='password')
        data = {'extended_list': True}
        response = self.client.get(self.api_url, data)
        self.assertContains(response, self.active_1.title)
        self.assertContains(response, self.active_2.title)
        self.assertContains(response, self.not_in_catalog.title)

    def test_user_can_only_see_public_courses_is_not_staff(self):
        self.user.is_staff = False
        self.user.save()
        self.client.login(username='user', password='password')
        data = {'extended_list': True}
        response = self.client.get(self.api_url, data)
        self.assertContains(response, self.active_1.title)
        self.assertContains(response, self.active_2.title)
        self.assertNotContains(response, self.not_in_catalog.title)

    def test_user_can_only_see_public_courses_is_not_logged_in(self):
        self.client.logout()
        data = {'extended_list': True}
        response = self.client.get(self.api_url, data)
        self.assertContains(response, self.active_1.title)
        self.assertContains(response, self.active_2.title)
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

    def test_university_score_available_only_if_logged_in_as_admin(self):
        university = UniversityFactory(code='test-university', score=10)
        CourseUniversityRelation.objects.create(
            course=self.active_1, university=university
        )
        filter_data = {'university': 'test-university'}
        self.login_as_admin()
        response = self.client.get(self.api_url, filter_data)
        response_data = json.loads(response.content)
        self.assertIn('score', response_data['results'][0]['universities'][0])
        self.client.logout()
        response = self.client.get(self.api_url, filter_data)
        response_data = json.loads(response.content)
        self.assertNotIn('score', response_data['results'][0]['universities'][0])

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

    def test_subjet_score_only_available_if_logged_in_as_admin(self):
        subject = CourseSubjectFactory(slug='test-subject')
        UniversityFactory(slug='another-subject')
        self.active_1.subjects.add(subject)
        filter_data = {'subject': 'test-subject'}
        self.login_as_admin()
        response = self.client.get(self.api_url, filter_data)
        response_data = json.loads(response.content)
        self.assertIn('score', response_data['results'][0]['subjects'][0])
        self.client.logout()
        response = self.client.get(self.api_url, filter_data)
        response_data = json.loads(response.content)
        self.assertNotIn('score', response_data['results'][0]['subjects'][0])

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

    def test_new_courses_exclude_courses_with_finished_enrollent(self):
        self.active_1.session_number = 1
        self.active_1.enrollment_end_date = now() - timedelta(days=1)
        self.active_1.save()
        self.active_2.session_number = 1
        self.active_2.enrollment_end_date = now() + timedelta(days=1)
        self.active_2.save()
        filter_data = {'availability': 'new'}
        response = self.client.get(self.api_url, filter_data)
        self.assertNotContains(response, self.active_1.title)
        self.assertContains(response, self.active_2.title)

    def test_public_api_results_do_not_include_score(self):
        self.client.logout()
        response = self.client.get(self.api_url)
        response_data = json.loads(response.content)
        self.assertNotIn('score', response_data['results'][0])

    def test_private_api_results_include_score(self):
        self.login_as_admin()
        response = self.client.get(self.api_url)
        response_data = json.loads(response.content)
        self.assertIn('score', response_data['results'][0])

    def test_enrollment_ends_soon(self):
        self.active_1.enrollment_end_date = self.soon
        self.active_1.save()
        self.active_2.enrollment_end_date = self.too_late
        self.active_2.save()
        filter_data = {'availability': 'enrollment-ends-soon'}
        response = self.client.get(self.api_url, filter_data)
        data = json.loads(response.content)
        self.assertEqual(1, len(data['results']))
        self.assertEqual(self.active_1.title, data['results'][0]['title'])

