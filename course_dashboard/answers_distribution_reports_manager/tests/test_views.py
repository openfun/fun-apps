from django.core.urlresolvers import reverse

from course_dashboard.tests.base import BaseCourseDashboardTestCase

class TestGradesReportManager(BaseCourseDashboardTestCase):

    def setUp(self):
        super(TestGradesReportManager, self).setUp()

        self.dashboard_url = reverse("course-dashboard:answers-distribution-reports-manager:dashboard",
                                     args=[self.course.id.to_deprecated_string()])
        self.generate_url = reverse("course-dashboard:answers-distribution-reports-manager:generate",
                                    args=[self.course.id.to_deprecated_string(),"33d5bb3f0c9949a2a494a7551da682fb"])

    def test_dashboard_view(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(200, response.status_code)
        
         
