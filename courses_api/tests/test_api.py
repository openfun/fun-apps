# -*- coding: utf-8 -*-

import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now, timedelta

from student.tests.factories import UserFactory


from courses import choices as courses_choices
from courses.models import CourseUniversityRelation
from courses.tests.factories import CourseFactory, CourseSubjectFactory

from fun.tests.utils import skipUnlessLms

from universities.tests.factories import UniversityFactory


@skipUnlessLms
class CourseAPITest(TestCase):

    def setUp(self):
        next_week = now() + timedelta(days=7)
        self.api_url = reverse('fun-courses-api:courses-list')
        self.active_1 = CourseFactory(
            title='active course 1',
            show_in_catalog=True,
            is_active=True,
            end_date=next_week,
        )
        self.active_2 = CourseFactory(
            title='active course 2',
            show_in_catalog=True,
            is_active=True,
            end_date=next_week,
        )
        self.not_active = CourseFactory(
            title='course not active',
            show_in_catalog=True,
            is_active=False,
            end_date=next_week,
        )
        self.not_in_catalog = CourseFactory(
            title='course not in catalog',
            show_in_catalog=False,
            is_active=True,
            end_date=next_week,
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

    def test_user_can_only_see_public_courses_if_not_staff(self):
        self.user.is_staff = False
        self.user.save()
        self.client.login(username='user', password='password')
        data = {'extended_list': True}
        response = self.client.get(self.api_url, data)
        self.assertContains(response, self.active_1.title)
        self.assertContains(response, self.active_2.title)
        self.assertNotContains(response, self.not_in_catalog.title)

    def test_user_can_only_see_public_courses_if_not_logged_in(self):
        self.client.logout()
        data = {'extended_list': True}
        response = self.client.get(self.api_url, data)
        self.assertContains(response, self.active_1.title)
        self.assertContains(response, self.active_2.title)
        self.assertNotContains(response, self.not_in_catalog.title)

    def test_courses_are_sorted_by_title(self):
        self.active_1.title = "z"
        self.active_2.title = "a"
        self.active_1.save()
        self.active_2.save()

        response = self.client.get(self.api_url, {
            "sort": "title"
        })
        courses = json.loads(response.content)["results"]
        self.assertLess(courses[0]["title"], courses[1]["title"])

    def test_courses_are_sorted_by_enrollment_date(self):
        self.active_1.score = 0
        self.active_2.score = 1
        self.active_1.enrollment_start_date = now() + timedelta(days=1)
        self.active_2.enrollment_start_date = now()
        self.active_1.save()
        self.active_2.save()

        response_increasing = self.client.get(self.api_url, {
            "sort": "enrollment_start_date"
        })
        response_decreasing = self.client.get(self.api_url, {
            "sort": "-enrollment_start_date"
        })
        courses_increasing = json.loads(response_increasing.content)["results"]
        courses_decreasing = json.loads(response_decreasing.content)["results"]

        self.assertLess(courses_increasing[0]["enrollment_start_date"],
                        courses_increasing[1]["enrollment_start_date"])
        self.assertGreater(courses_decreasing[0]["enrollment_start_date"],
                           courses_decreasing[1]["enrollment_start_date"])

    def test_courses_are_sorted_by_start_date(self):
        self.active_1.score = 0
        self.active_2.score = 1
        self.active_1.start_date = now() + timedelta(days=1)
        self.active_2.start_date = now()
        self.active_1.save()
        self.active_2.save()

        response_increasing = self.client.get(self.api_url, {
            "sort": "start_date"
        })
        response_decreasing = self.client.get(self.api_url, {
            "sort": "-start_date"
        })
        courses_increasing = json.loads(response_increasing.content)["results"]
        courses_decreasing = json.loads(response_decreasing.content)["results"]

        self.assertLess(courses_increasing[0]["start_date"],
                        courses_increasing[1]["start_date"])
        self.assertGreater(courses_decreasing[0]["start_date"],
                           courses_decreasing[1]["start_date"])

    def test_courses_are_sorted_by_score_with_incorrect_order_by(self):
        self.active_1.score = 1
        self.active_2.score = 2
        self.active_1.title = "1"
        self.active_2.title = "2"
        self.active_1.save()
        self.active_2.save()
        response = self.client.get(self.api_url, {
            "sort": "invalidvalue"
        })
        courses = json.loads(response.content)["results"]
        self.assertEqual(self.active_2.title, courses[0]["title"])
        self.assertEqual(self.active_1.title, courses[1]["title"])

    def test_can_update_course_score_as_admin(self):
        self.login_as_admin()
        self.active_1.score = 0
        self.active_1.save()
        data = {'score': 100}
        url = reverse('fun-courses-api:courses-detail',
            args=[self.active_1.id]
        )
        response = self.client.put(url, data)
        response_data = json.loads(response.content)
        self.assertEqual(100, response_data['score'])

    def test_cannot_update_course_score_if_not_logged_in(self):
        self.client.logout()
        data = {'score': 100}
        url = reverse('fun-courses-api:courses-detail',
            args=[self.active_1.id]
        )
        response = self.client.put(url, data)
        self.assertNotEqual(response.status_code, 200)

    def test_cannot_update_course_if_set_as_prevent_auto_update(self):
        self.login_as_admin()
        self.active_1.prevent_auto_update = True
        self.active_1.save()
        data = {'score': 100}
        url = reverse('fun-courses-api:courses-detail',
            args=[self.active_1.id]
        )
        response = self.client.put(url, data)
        self.assertNotEqual(response.status_code, 200)

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

    def test_ended_courses_are_listed_at_the_end(self):
        yesterday = now() - timedelta(days=1)
        tomorrow = now() + timedelta(days=1)
        self.active_1.end_date = yesterday
        self.active_2.end_date = tomorrow
        self.active_1.score = self.active_2.score + 1
        self.active_1.save()
        self.active_2.save()

        response = self.client.get(self.api_url, {})
        data = json.loads(response.content)

        self.assertEqual(2, data["count"])
        self.assertEqual(self.active_2.id, data["results"][0]["id"])
        self.assertEqual(self.active_1.id, data["results"][1]["id"])

    def test_enrollment_ended_courses_are_listed_at_the_end(self):
        yesterday = now() - timedelta(days=1)
        tomorrow = now() + timedelta(days=1)
        self.active_1.end_date = tomorrow
        self.active_2.end_date = tomorrow
        self.active_1.enrollment_end_date = yesterday
        self.active_2.enrollment_end_date = tomorrow
        self.active_1.score = self.active_2.score + 1
        self.active_1.save()
        self.active_2.save()

        response = self.client.get(self.api_url, {})
        data = json.loads(response.content)

        self.assertEqual(2, data["count"])
        self.assertEqual(self.active_2.id, data["results"][0]["id"])
        self.assertEqual(self.active_1.id, data["results"][1]["id"])
