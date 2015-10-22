# -*- coding: utf-8 -*-

from django.test import TestCase

from fun.tests.utils import skipUnlessLms
from courses import managers
from courses import models

from . import factories


@skipUnlessLms
class TestCourseSubject(TestCase):

    def test_annotate_with_public_courses(self):
        course1 = factories.CourseFactory.create(key="key1", is_active=False, show_in_catalog=False)
        course2 = factories.CourseFactory.create(key="key2", is_active=True, show_in_catalog=False)
        course3 = factories.CourseFactory.create(key="key3", is_active=True, show_in_catalog=True)
        course4 = factories.CourseFactory.create(key="key4", is_active=True, show_in_catalog=True)

        subject1 = factories.CourseSubjectFactory.create(score=1, slug="slug1")
        subject2 = factories.CourseSubjectFactory.create(score=2, slug="slug2")
        subject3 = factories.CourseSubjectFactory.create(score=3, slug="slug3")
        subject4 = factories.CourseSubjectFactory.create(score=4, slug="slug4")

        course1.subjects.add(subject1)
        course2.subjects.add(subject2)
        course3.subjects.add(subject3)
        course4.subjects.add(subject4)

        subjects = managers.annotate_with_public_courses(models.CourseSubject.objects.all())

        self.assertEqual(2, len(subjects))
        self.assertEqual(subject4.pk, subjects[0].pk)
        self.assertEqual(subject3.pk, subjects[1].pk)
        self.assertEqual(1, subjects[0].public_courses_count)
        self.assertEqual(1, subjects[1].public_courses_count)
