from datetime import datetime

from django.test.utils import override_settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import TEST_DATA_MOCK_MODULESTORE

from course_dashboard import views
from .base import BaseCourseDashboardTestCase


@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class EnrollmentStatsTestCase(BaseCourseDashboardTestCase):

    def get_course_enrollment_stats(self, course, response_format=None):
        return self.get_course_url("course-dashboard:enrollment-stats", course, response_format=response_format)

    def get_enrollment_stats(self, course_id, response_format=None):
        return self.get_url("course-dashboard:enrollment-stats", course_id, response_format=response_format)

    def test_empty_enrollment_stats(self):
        response = self.get_course_enrollment_stats(self.course)
        self.assertEqual(200, response.status_code)

    def test_enrollment_stats(self):
        self.enroll_student(self.course)
        response = self.get_course_enrollment_stats(self.course)
        self.assertEqual(200, response.status_code)

    def test_enrollment_stats_for_non_existing_course_raises_404(self):
        response = self.get_enrollment_stats("not/really/there")
        self.assertEqual(404, response.status_code)

    def test_student_has_no_access(self):
        student = UserFactory.create()
        self.client.login(username=student.username, password="test")
        response = self.get_course_enrollment_stats(self.course)
        self.assertEqual(404, response.status_code)

    def test_staff_member_has_access(self):
        student = UserFactory.create(is_staff=True)
        self.client.login(username=student.username, password="test")
        response = self.get_course_enrollment_stats(self.course)
        self.assertEqual(200, response.status_code)

    def test_inactive_staff_user_has_no_access(self):
        student = UserFactory.create(is_staff=True, is_active=False)
        self.client.logout()
        self.client.login(username=student.username, password="test")
        response = self.get_course_enrollment_stats(self.course)
        self.assertEqual(404, response.status_code)

    def test_csv_response(self):
        course_enrollment = self.enroll_student(self.course)
        enrolled_at = datetime(year=2015, month=1, day=1, tzinfo=timezone.UTC())
        course_enrollment.created = enrolled_at
        course_enrollment.save()

        response = self.get_course_enrollment_stats(self.course, response_format="csv")
        rows = self.get_csv_response_rows(response)

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(rows))
        self.assertEqual(["2015/01/01", "1"], rows[1])


class StudentMapTestCase(BaseCourseDashboardTestCase):

    def get_course_student_map(self, course, response_format=None):
        return self.get_course_url("course-dashboard:student-map", course, response_format=response_format)

    def get_student_map(self, course_id, response_format=None):
        return self.get_url("course-dashboard:student-map", course_id, response_format=response_format)

    def test_student_map(self):
        response = self.get_course_student_map(self.course)

        self.assertEqual(200, response.status_code)

    def test_student_map_for_non_existing_course_raises_404(self):
        response = self.get_student_map("not/really/there")
        self.assertEqual(404, response.status_code)

    def test_non_empty_student_map(self):
        self.enroll_student(self.course, user__profile__country='FR')
        response = self.get_course_student_map(self.course)
        self.assertEqual(200, response.status_code)
        self.assertIn("France", response.content)

    def test_get_country_name(self):
        self.assertEqual(_("France"), views.get_country_name('FR'))
        self.assertEqual(_("Unknown"), views.get_country_name(''))

    def test_student_has_no_access(self):
        student = UserFactory.create()
        self.client.login(username=student.username, password="test")
        response = self.get_course_student_map(self.course)
        self.assertEqual(404, response.status_code)

    def test_staff_member_has_access(self):
        student = UserFactory.create(is_staff=True)
        self.client.login(username=student.username, password="test")
        response = self.get_course_student_map(self.course)
        self.assertEqual(200, response.status_code)

    def test_csv_response(self):
        self.enroll_student(self.course, user__profile__country='FR')

        response = self.get_course_student_map(self.course, response_format="csv")
        rows = self.get_csv_response_rows(response)

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(rows))
        self.assertEqual([_("France"), "1"], rows[1])
