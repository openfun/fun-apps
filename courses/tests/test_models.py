# -*- coding: utf-8 -*-

from django.test import TestCase

from fun.tests.utils import skipUnlessLms
from courses import managers
from courses import models

from . import factories


@skipUnlessLms
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
