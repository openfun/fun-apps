from datetime import datetime

from django.utils import timezone

from microsite_configuration import microsite
from student.tests.factories import CourseEnrollmentFactory
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory

import course_dashboard.stats as stats
from fun.utils import countries
from fun.tests.utils import setMicrositeTestSettings

from .base import BaseCourseDashboardTestCase


class StatsTestCase(BaseCourseDashboardTestCase):
    def setUp(self):
        super(StatsTestCase, self).setUp()
        self.user = UserFactory()

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

    def test_null_countries_are_counted(self):
        course = CourseFactory.create()
        course_id = self.get_course_id(course)
        CourseEnrollmentFactory.create(course_id=course_id, user__profile__country=None)
        CourseEnrollmentFactory.create(course_id=course_id, user__profile__country=None)

        course_population = stats.population_by_country(course_id)
        self.assertEqual(1, len(course_population))
        self.assertEqual(2, course_population[countries.UNKNOWN_COUNTRY_CODE])

    def test_dependent_territories_are_not_listed_separately(self):
        course = CourseFactory.create()
        self.enroll_student(course, user__profile__country='GF', user__is_active=False)
        self.enroll_student(course, user__profile__country='PF', user__is_active=False)
        course_population = stats.population_by_country(self.get_course_id(course))
        self.assertEqual({'FR': 2}, course_population)

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

    def test_most_active_username(self):
        threads = [
            {"username": 1},
            {"username": 1},
            {"username": 2},
        ]
        self.assertEqual(1, stats.most_active_username(threads))

    @setMicrositeTestSettings
    def test_enrollment_stats_with_microsite_configuration(self):
        self.enroll_student(user=UserFactory(),
                            course=CourseFactory.create(org=microsite.get_value('course_org_filter')))
        self.enroll_student(user=self.user,
                            course=self.course)
        self.assertEqual(stats.active_enrollments().count(), 1)
