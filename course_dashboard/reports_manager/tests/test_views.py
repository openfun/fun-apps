import os
import shutil
from unittest import skip

from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings

from course_dashboard.tests.base import BaseCourseDashboardTestCase


@override_settings(SHARED_ROOT='/tmp/shared-test/')
class TestViewsReportManager(BaseCourseDashboardTestCase):
    def setUp(self):
        super(TestViewsReportManager, self).setUp()
        if os.path.exists(settings.SHARED_ROOT):
            shutil.rmtree(settings.SHARED_ROOT)
        self.dashboard_url = reverse("course-dashboard:reports-manager:dashboard",
                                     args=[self.course.id.to_deprecated_string()])

    def tearDown(self):
        if os.path.exists(settings.SHARED_ROOT):
            shutil.rmtree(settings.SHARED_ROOT)

    def get_url_for_generate_view(self, problem_module):
        generate_url = reverse("course-dashboard:reports-manager:generate",
                               args=[self.course.id.to_deprecated_string(),
                                     problem_module.location.name])
        return generate_url


    # TODO Dogwood: re-enable this test
    @skip('Causing TransactionManagementError: Cannot be inside an atomic block. in dogwood')
    def test_generate(self):
        response = self.client.get(self.get_url_for_generate_view(self.problem_module))
        self.assertEqual(response.status_code, 302)

    def test_dashboard(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
