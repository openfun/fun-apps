from datetime import datetime

from django.test.utils import override_settings
from django.utils import timezone

from student.tests.factories import CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import TEST_DATA_MOCK_MODULESTORE
from xmodule.modulestore.tests.factories import CourseFactory

import course_dashboard.stats as stats
from .base import BaseCourseDashboardTestCase


@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class StatsTestCase(BaseCourseDashboardTestCase):

    def test_average_enrollments(self):
        self.enroll_student_at(self.course, 2015, 2, 2)
        self.enroll_student_at(self.course, 2015, 2, 3)
        enrollments = stats.EnrollmentStats(self.get_course_id(self.course))

        self.assertEqual(2, enrollments.day_span())
        self.assertEqual(1, enrollments.daily_average())

    def test_population_by_country_for_empty_course(self):
        course = CourseFactory.create()
        course_population = stats.population_by_country(self.get_course_id(course))
        self.assertEqual({}, course_population)

    def test_population_by_country_for_non_empty_course(self):
        course = CourseFactory.create()
        empty_course = CourseFactory.create()
        course_id = self.get_course_id(course)
        empty_course_id = self.get_course_id(empty_course)
        CourseEnrollmentFactory.create(course_id=course_id, user__profile__country='FR')

        empty_course_population = stats.population_by_country(empty_course_id)
        course_population = stats.population_by_country(course_id)

        self.assertEqual({}, empty_course_population)
        self.assertEqual({'FR': 1}, course_population)

    def test_inactive_students_are_included_but_not_inactive_enrollments(self):
        course = CourseFactory.create()
        self.enroll_student(course, user__profile__country='FR', user__is_active=False)
        self.enroll_student(course, user__profile__country='US', is_active=False)
        course_population = stats.population_by_country(self.get_course_id(course))
        self.assertEqual({'FR': 1}, course_population)

    def test_inactive_enrollments_are_not_included(self):
        course = CourseFactory.create()
        self.enroll_student(course, user__profile__country='FR', user__is_active=False)
        course_population = stats.population_by_country(self.get_course_id(course))
        self.assertEqual({'FR': 1}, course_population)

    def enroll_student_at(self, course, year, month, day, **kwargs):
        # For some reason, the course enrollment factory does not set the
        # proper creation date so we need to set it manually
        enrollment = self.enroll_student(course, **kwargs)
        enrollment.created = datetime(year, month, day, tzinfo=timezone.UTC())
        enrollment.save()

    def test_forum_threads_per_day(self):
        threads = [{
            "created_at": '2015-02-03T18:00:00Z'
        }]
        threads_per_day = stats.forum_threads_per_day(threads)
        self.assertEqual([(datetime(year=2015, month=2, day=3), 1)], threads_per_day)
