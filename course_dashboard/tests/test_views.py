from bs4 import BeautifulSoup

from certificates.tests.factories import GeneratedCertificateFactory
from certificates.models import CertificateStatuses

from django.utils.translation import ugettext_lazy as _

from student.tests.factories import UserFactory

from .base import BaseCourseDashboardTestCase


class StudentMapTestCase(BaseCourseDashboardTestCase):

    def get_course_student_map(self, course, response_format=None):
        return self.get_response("course-dashboard:student-map", course, response_format=response_format)

    def get_student_map(self, course_id, response_format=None):
        return self.get_course_id_response("course-dashboard:student-map", course_id, response_format=response_format)

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

class CertificateStatsTestCase(BaseCourseDashboardTestCase):
    def setUp(self):
        super(CertificateStatsTestCase, self).setUp()

        # if we generate only one document for each, we won't know if we used a value in the wrong case
        GeneratedCertificateFactory(course_id=self.course.id, user=UserFactory(),
                                    status=CertificateStatuses.notpassing)

        for _ in range(2):
            GeneratedCertificateFactory(course_id=self.course.id, user=UserFactory(),
                                        status=CertificateStatuses.downloadable)

        for _ in range(3):
            GeneratedCertificateFactory(course_id=self.course.id, user=UserFactory(),
                                        status=CertificateStatuses.notpassing, mode="verified")

        for _ in range(4):
            GeneratedCertificateFactory(course_id=self.course.id, user=UserFactory(),
                                        status=CertificateStatuses.downloadable, mode="verified")

        self.response = self.get_response("course-dashboard:certificate-stats", self.course)


    def test_total_is_correct(self):
        soup = BeautifulSoup(self.response.content)
        self.assertEqual(u"10", soup.find("td", {"id": "total"}).text)

    def test_marginals_are_correct(self):
        soup = BeautifulSoup(self.response.content)
        self.assertEqual(u"6", soup.find("td", {"id": "total-passing"}).text)
        self.assertEqual(u"4", soup.find("td", {"id": "total-not-passing"}).text)
        self.assertEqual(u"7", soup.find("td", {"id": "total-verified"}).text)
        self.assertEqual(u"3", soup.find("td", {"id": "total-honor"}).text)
