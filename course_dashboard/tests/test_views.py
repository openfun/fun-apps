from bs4 import BeautifulSoup

from certificates.tests.factories import GeneratedCertificateFactory
from certificates.models import CertificateStatuses

from django.utils.translation import ugettext_lazy as _

from student.tests.factories import UserFactory

from .base import BaseCourseDashboardTestCase


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
