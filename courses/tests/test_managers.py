# -*- coding: utf-8 -*-

from random import randint

from django.test import TestCase
from django.utils.timezone import now, timedelta

from universities.tests.factories import UniversityFactory

from ..models import Course
from .factories import CourseFactory, CourseUniversityRelationFactory


class CourseManagerTestCase(TestCase):

    def test_courses_manager_university_courses_public(self):
        """
        The "public" query appended to the query to get a university's courses
        should return only public courses for this university.
        """
        # Create 2 universities
        university1, university2 = UniversityFactory.create_batch(
            2, detail_page_enabled=True, is_obsolete=False, score=1)

        # Create public courses for each university and both
        course_u1, course_u2, course_u1u2 = CourseFactory.create_batch(
            3, show_in_catalog=True)
        # ... and link courses to university 1
        CourseUniversityRelationFactory(course=course_u1, university=university1)
        CourseUniversityRelationFactory(course=course_u2, university=university2)
        CourseUniversityRelationFactory(course=course_u1u2, university=university1)
        CourseUniversityRelationFactory(course=course_u1u2, university=university2)

        # Create private courses for each university and both
        course_pu1, course_pu2, course_pu1u2 = CourseFactory.create_batch(
            3, show_in_catalog=False)
        # ... and link courses to university 2
        CourseUniversityRelationFactory(course=course_pu1, university=university1)
        CourseUniversityRelationFactory(course=course_pu2, university=university2)
        CourseUniversityRelationFactory(course=course_pu1u2, university=university1)
        CourseUniversityRelationFactory(course=course_pu1u2, university=university2)

        self.assertEqual(set(university1.courses.all()), {
            course_u1, course_u1u2, course_pu1, course_pu1u2})
        self.assertEqual(set(university2.courses.all()), {
            course_u2, course_u1u2, course_pu2, course_pu1u2})

        self.assertEqual(set(university1.courses.public()), {course_u1, course_u1u2})
        self.assertEqual(set(university2.courses.public()), {course_u2, course_u1u2})

    def test_courses_manager_annotate_for_ordering_course_has_ended(self):
        """
        A course that has ended should be annotated with a "has_ended" flag set to True.
        """
        past = now() - timedelta(minutes=1)
        CourseFactory(start_date=past - timedelta(days=30), end_date=past)
        query = Course.objects.annotate_for_ordering()
        self.assertEqual(query[0].has_ended, True)

    def test_courses_manager_annotate_for_ordering_course_has_ended_no_end(self):
        """
        A course with no end date should be annotated with a "has_ended" flag set to True.
        """
        CourseFactory(end_date=None)
        query = Course.objects.annotate_for_ordering()
        self.assertEqual(query[0].has_ended, False)

    def test_courses_manager_annotate_for_ordering_course_has_not_ended(self):
        """
        A course that has not ended yet should be annotated with a "has_ended" flag set to False.
        """
        future = now() + timedelta(minutes=1)
        CourseFactory(start_date=future - timedelta(days=30), end_date=future)
        query = Course.objects.annotate_for_ordering()
        self.assertEqual(query[0].has_ended, False)

    def test_courses_manager_annotate_for_ordering_course_enrollment_over(self):
        """
        A course for which enrollment is finished should be annotated with a
        "is_enrollment_over" flag set to True.
        """
        past = now() - timedelta(minutes=1)
        CourseFactory(enrollment_end_date=past)
        query = Course.objects.annotate_for_ordering()
        self.assertEqual(query[0].is_enrollment_over, True)

    def test_courses_manager_annotate_for_ordering_course_enrollment_over_no_date(self):
        """
        A course with no end of enrollment date should be annotated with a
        "is_enrollment_over" flag set to False.
        """
        CourseFactory(enrollment_end_date=None)
        query = Course.objects.annotate_for_ordering()
        self.assertEqual(query[0].is_enrollment_over, False)

    def test_courses_manager_annotate_for_ordering_course_enrollment_not_over(self):
        """
        A course for which the enrollment period is not finished yet should be annotated
        with a "is_enrollment_over" flag set to False.
        """
        future = now() + timedelta(minutes=1)
        CourseFactory(enrollment_end_date=future)
        query = Course.objects.annotate_for_ordering()
        self.assertEqual(query[0].is_enrollment_over, False)

    def test_courses_manager_annotate_for_ordering_start_date_past_ordering_date(self):
        """
        A course for which the start date is in the past should be annotated with an
        ordering date equal to its end of enrollment date.
        """
        past = now() - timedelta(minutes=1)
        course = CourseFactory(start_date=past)
        query = Course.objects.annotate_for_ordering()
        # ordering_date is in raw SQL format. It's good enough for ordering but we ignore
        # milliseconds before comparing them to django datetimes as they trunk milliseconds
        # when they are equal to 0.
        self.assertEqual(
            query[0].ordering_date[:19], course.enrollment_end_date.strftime('%Y-%m-%d %H:%M:%S'))

    def test_courses_manager_annotate_for_ordering_start_date_future_ordering_date(self):
        """
        A course for which the start date is in the future should be annotated with an
        ordering date equal to its start date.
        """
        future = now() + timedelta(minutes=1)
        course = CourseFactory(start_date=future)
        query = Course.objects.annotate_for_ordering()
        # ordering_date is in raw SQL format. It's good enough for ordering but we ignore
        # milliseconds before comparing them to django datetimes as they trunk milliseconds
        # when they are equal to 0.
        self.assertEqual(
            query[0].ordering_date[:19], course.start_date.strftime('%Y-%m-%d %H:%M:%S'))

    def test_courses_manager_annotate_for_ordering_no_start_date_ordering_date(self):
        """
        A course for which the start date is not defined should be annotated with an ordering
        date equal to its end of enrollment date.
        """
        course = CourseFactory(
            start_date=None, enrollment_end_date=now() + timedelta(days=randint(0, 30)))
        query = Course.objects.annotate_for_ordering()
        # ordering_date is in raw SQL format. It's good enough for ordering but we must ignore
        # milliseconds before comparing them to django datetimes as they trunk milliseconds
        # when they are equal to 0.
        self.assertEqual(
            query[0].ordering_date[:19], course.enrollment_end_date.strftime('%Y-%m-%d %H:%M:%S'))

    def test_courses_manager_annotate_for_ordering_apply(self):
        """
        Ordering applied on the annotated field "ordering_date" should work as expected.
        """
        # Create some dates:
        #   - the name indicates if they are in the past or in the future,
        #   - the index indicates how these 8 dates are ordered: 1 first, 8 last.
        past3, past2, past1 = (now() - timedelta(minutes=i+1) for i in range(3))
        future4, future5, future6, future7, future8 = (
            now() + timedelta(minutes=i+1) for i in range(5))

        # Create courses with a start date in the future and with a different ordering
        # on the enrollment end date
        course_a = CourseFactory(start_date=future4, enrollment_end_date=future6)
        course_b = CourseFactory(start_date=future6, enrollment_end_date=future5)
        course_c = CourseFactory(start_date=future7, enrollment_end_date=past1)

        # Create courses with a start date in the future and with a different ordering
        # on the enrollment end date
        course_d = CourseFactory(start_date=past1, enrollment_end_date=future8)
        course_e = CourseFactory(start_date=past2, enrollment_end_date=past3)
        course_f = CourseFactory(start_date=past3, enrollment_end_date=future5)

        ordered_courses = Course.objects.annotate_for_ordering().order_by('ordering_date')
        self.assertEqual(list(ordered_courses), [
            course_e, course_a, course_f, course_b, course_c, course_d])
