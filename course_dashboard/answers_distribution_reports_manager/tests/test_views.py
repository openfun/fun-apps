import os
import shutil

from django.core.urlresolvers import reverse
from django.conf import settings
from django.test.utils import override_settings

from xmodule.modulestore.tests.factories import ItemFactory

from backoffice.utils import get_course_key
from course_dashboard.answers_distribution_reports_manager import utils
from course_dashboard.tests.base import BaseCourseDashboardTestCase

from fun import shared

@override_settings(SHARED_ROOT='/tmp/shared-test/')
class TestGradesReportManager(BaseCourseDashboardTestCase):

    def setUp(self):
        super(TestGradesReportManager, self).setUp()
        if os.path.exists(settings.SHARED_ROOT):
            shutil.rmtree(settings.SHARED_ROOT)
        self.dashboard_url = reverse("course-dashboard:answers-distribution-reports-manager:dashboard",
                                     args=[self.course.id.to_deprecated_string()])

    def tearDown(self):
        if os.path.exists(settings.SHARED_ROOT):
            shutil.rmtree(settings.SHARED_ROOT)

    def get_url_for_generate_view(self, problem_module):
        generate_url = reverse("course-dashboard:answers-distribution-reports-manager:generate",
                               args=[self.course.id.to_deprecated_string(),
                                     problem_module.scope_ids.usage_id.name])
        return generate_url

    def test_dashboard_view(self):
        response = self.client.get(self.dashboard_url)
        self.assertEqual(200, response.status_code)

    def test_generate_answers_distribution_report_with_long_filename(self):
        course_key = get_course_key(self.get_course_id(self.course))

        chapter = ItemFactory(course=self.course, category='chapter',
                              display_name='c'*128)
        sequential = ItemFactory(parent=chapter, category='sequential',
                                 display_name='s'*128)
        vertical = ItemFactory(parent=sequential, category='vertical',
                               display_name='v'*128)
        problem_module = ItemFactory(parent=vertical, category='problem',
                                     display_name=None)

        # generate report
        self.client.get(self.get_url_for_generate_view(problem_module))

        # test if the corresponding report was saved on the filesystem
        files = utils.get_answers_distribution_reports_from_course(course_key)
        file_path = shared.get_path(utils.ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY,
                                    course_key.org, course_key.course,
                                    files[0])
        self.assertTrue(os.path.isfile(file_path))
