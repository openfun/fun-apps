import codecs
import os
import shutil
import unicodecsv

from mock import Mock, patch
from django.contrib.auth.models import User
from django.conf import settings
from django.test.utils import override_settings

from student.models import UserProfile
from student.tests.factories import UserFactory
from courseware.tests.factories import StudentModuleFactory
from instructor_task.tests.test_base import InstructorTaskModuleTestCase, OPTION_1, OPTION_2
from instructor_task.tests.test_tasks import PROBLEM_URL_NAME

from course_dashboard.problem_stats.tests.problem_monitor import ProblemMonitorTestCase
from course_dashboard.reports_manager.tasks import generate_answers_distribution_report, get_path
from course_dashboard.reports_manager.utils import build_answers_distribution_report_name

@override_settings(SHARED_ROOT='/tmp/shared-test')
class AnswersDistributionReportsTask(InstructorTaskModuleTestCase, ProblemMonitorTestCase):

    def setUp(self):
        super(AnswersDistributionReportsTask, self).setUp()
        self.initialize_course()
        self.define_option_problem(problem_url_name=PROBLEM_URL_NAME)
        self.problem_module = self.store.get_item(self.problem_location(PROBLEM_URL_NAME))

    def _read_report_file(self, filepath):
        with codecs.open(filepath, 'r', 'utf-8') as report:
            reader = unicodecsv.reader(report, encoding='utf-8')
            rows = list(reader)
        return rows

    def tearDown(self):
        if os.path.exists(settings.SHARED_ROOT):
            shutil.rmtree(settings.SHARED_ROOT)
