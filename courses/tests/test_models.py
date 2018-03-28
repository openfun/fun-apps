# -*- coding: utf-8 -*-

import datetime
from django.test import TestCase
from django.utils.timezone import now, timedelta

from courses import managers
from courses import models

from . import factories
from universities.tests.factories import UniversityFactory


class TestCourseSubject(TestCase):

    def test_ability_to_count_public_courses_for_course_subjects(self):
        course_not_active = factories.CourseFactory.create(
            key="key1", is_active=False, show_in_catalog=False
        )
        course_not_in_catalog = factories.CourseFactory.create(
            key="key2", is_active=True, show_in_catalog=False
        )
        course_active_1 = factories.CourseFactory.create(
            key="key3", is_active=True, show_in_catalog=True
        )
        course_active_2 = factories.CourseFactory.create(
            key="key4", is_active=True, show_in_catalog=True
        )

        subject_not_active = factories.CourseSubjectFactory.create(
            score=1, slug="not-active"
        )
        subject_not_in_catalog = factories.CourseSubjectFactory.create(
            score=2, slug="not-in-catalog"
        )
        subject_active_1 = factories.CourseSubjectFactory.create(
            score=3, slug="active-1"
        )
        subject_active_2 = factories.CourseSubjectFactory.create(
            score=4, slug="active-2"
        )

        course_not_active.subjects.add(subject_not_active)
        course_not_in_catalog.subjects.add(subject_not_in_catalog)
        course_active_1.subjects.add(subject_active_1)
        course_active_2.subjects.add(subject_active_2)

        subjects = managers.annotate_with_public_courses(models.CourseSubject.objects.all())

        self.assertNotIn(subject_not_active, subjects)
        self.assertNotIn(subject_not_in_catalog, subjects)
        self.assertIn(subject_active_1, subjects)
        self.assertIn(subject_active_2, subjects)
        self.assertEqual(1, subjects.get(slug='active-1').public_courses_count)
        self.assertEqual(1, subjects.get(slug='active-2').public_courses_count)

    def test_new_courses_filter(self):
        factories.CourseFactory.create(session_number=2)
        course_new = factories.CourseFactory.create(
            session_number=1, is_active=True, show_in_catalog=True,
            enrollment_end_date=datetime.datetime.now() + datetime.timedelta(days=1))
        new_courses = list(models.Course.objects.new())
        self.assertEqual([course_new], new_courses)

    def test_get_course_language(self):
        course = factories.CourseFactory.create(language="en")

        self.assertEqual("en",
                         models.Course.get_course_language(unicode(course.key)))

        self.assertEqual(None,
                         models.Course.get_course_language(unicode("this/course/doesNotExist")))

    def test_number_of_queries_of_with_related(self):
        # Create a large number of course objects
        for _ in range(0, 10):
            factories.CourseFactory.create()

        # The number of SQL queries required to load the first university and
        # its name should not be proportional to the number of objects in the
        # database.
        with self.assertNumQueries(4):
            for course in models.Course.objects.with_related():
                _first_university = course.get_first_university()
                _university_name = course.university_name

    def test_annotate_with_is_enrollment_over(self):
        yesterday = now() - timedelta(days=1)
        tomorrow = now() + timedelta(days=1)
        course_enrollment_ended = factories.CourseFactory.create(enrollment_end_date=yesterday)
        course_enrollment_not_ended = factories.CourseFactory.create(enrollment_end_date=tomorrow)
        course_open = factories.CourseFactory.create(enrollment_end_date=None)
        queryset = models.Course.objects.annotate_with_is_enrollment_over()

        # Note: we do not use assertTrue and assertFalse here because we want
        # to make sure is_enrollment_over is not None
        self.assertEqual(True, queryset.get(id=course_enrollment_ended.id).is_enrollment_over)
        self.assertEqual(False, queryset.get(id=course_enrollment_not_ended.id).is_enrollment_over)
        self.assertEqual(False, queryset.get(id=course_open.id).is_enrollment_over)


class TestCourseManager(TestCase):
    def setUp(self):
        self.u1 = UniversityFactory.create(detail_page_enabled=True, is_obsolete=False, score=1)
        self.u2 = UniversityFactory.create(detail_page_enabled=True, is_obsolete=False, score=1)

    def test_university_public_courses_should_contain_only_public_courses(self):
        course_public = factories.CourseFactory.create()
        course_private = factories.CourseFactory.create(show_in_catalog=False)
        factories.CourseUniversityRelationFactory(course=course_public, university=self.u1)
        factories.CourseUniversityRelationFactory(course=course_private, university=self.u1)

        self.assertIn(course_public, self.u1.courses.public())
        self.assertNotIn(course_private, self.u1.courses.public())
        self.assertIn(course_public, self.u1.courses.all())
        self.assertIn(course_private, self.u1.courses.all())

    def test_public_courses_from_one_university_should_only_contain_courses_from_this_university(self):
        course_u1 = factories.CourseFactory.create()
        course_u1u2 = factories.CourseFactory.create()
        course_u2 = factories.CourseFactory.create()

        factories.CourseUniversityRelationFactory(course=course_u1, university=self.u1)
        factories.CourseUniversityRelationFactory(course=course_u2, university=self.u2)
        factories.CourseUniversityRelationFactory(course=course_u1u2, university=self.u1)
        factories.CourseUniversityRelationFactory(course=course_u1u2, university=self.u2)

        self.assertIn(course_u1, self.u1.courses.public())
        self.assertIn(course_u1u2, self.u1.courses.public())

        self.assertIn(course_u2, self.u2.courses.public())
        self.assertIn(course_u1u2, self.u2.courses.public())

        self.assertNotIn(course_u2, self.u1.courses.public())
        self.assertNotIn(course_u1, self.u2.courses.public())

        self.assertEqual(set(self.u1.courses.all()), set(self.u1.courses.public()))
        self.assertEqual(set(self.u2.courses.all()), set(self.u2.courses.public()))

