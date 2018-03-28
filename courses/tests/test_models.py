# -*- coding: utf-8 -*-

import datetime
from django.test import TestCase

from courses import managers
from courses import models

from . import factories


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
                course.get_first_university()
                course.university_name
