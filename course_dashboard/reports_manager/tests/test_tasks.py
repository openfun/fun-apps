import csv

import json
import os
import shutil

from mock import patch
from django.conf import settings
from django.test.utils import override_settings

from student.models import UserProfile, anonymous_id_for_user
from student.tests.factories import UserFactory
from courseware.tests.factories import StudentModuleFactory
from instructor_task.tests.test_base import InstructorTaskModuleTestCase, OPTION_1, OPTION_2

from course_dashboard.problem_stats.tests.test_problem_monitor import ProblemMonitorTestCase
from course_dashboard.reports_manager.tasks import generate_answers_distribution_report, get_path
from course_dashboard.reports_manager.utils import build_answers_distribution_report_name, anonymize_username

from fun.tests.utils import skipUnlessLms

@skipUnlessLms
@override_settings(SHARED_ROOT='/tmp/shared-test-answers-distribution')
class AnswersDistributionReportsTask(InstructorTaskModuleTestCase, ProblemMonitorTestCase):
    def setUp(self):
        from instructor_task.tests.test_tasks import PROBLEM_URL_NAME

        super(AnswersDistributionReportsTask, self).setUp()
        self._rm_tree()
        self.initialize_course()
        self.define_option_problem(problem_url_name=PROBLEM_URL_NAME)
        self.problem_module = self.store.get_item(self.problem_location(PROBLEM_URL_NAME,
                                                                        self.course.id))
        self.running_report_name = build_answers_distribution_report_name(self.problem_module)
        self.username = 'joe'

    def _rm_tree(self):
        if os.path.exists(settings.SHARED_ROOT):
            shutil.rmtree(settings.SHARED_ROOT)

    def _launch_task(self):
        task_input = {'problem_id' : self.problem_module.location.name,
                      'running_report_name' : self.running_report_name}

        with patch('instructor_task.tasks_helper._get_current_task'):
            generate_answers_distribution_report(None, self.course.id,
                                                 task_input, None)

    def _create_student_module_entry(self):
        cmap = self._build_correct_map('correct')
        student_answers = self._build_student_answers(OPTION_1, OPTION_2)

        StudentModuleFactory(course_id=self.course.id,
                             module_state_key=self.problem_module.location,
                             student=UserFactory(username=self.username,
                                                 profile__year_of_birth=1989,
                                                 profile__level_of_education=u'bac'),
                             state=json.dumps(self._build_student_module_state(cmap, student_answers)))

    def _read_report_file(self, filepath):
        with open(filepath, 'r') as report:
            reader = csv.reader(report)
            rows = list(reader)
        return rows

    def _create_response_row(self):
        user_profile = UserProfile.objects.get(user__username=self.username)
        response_row = [unicode(x) for x in [anonymize_username(user_profile.user.username),
                                             anonymous_id_for_user(user_profile.user, self.course.id),
                                             user_profile.gender, user_profile.year_of_birth,
                                             user_profile.level_of_education]] + [OPTION_1, OPTION_2]
        return response_row

    def test_generate_answers_distribution_report(self):
        self._create_student_module_entry()

        self._launch_task()
        rows = self._read_report_file(get_path(self.running_report_name,
                                               self.problem_module.location))

        self.assertEqual(rows[1], ['id', 'course_specific_id', 'gender', 'year_of_birth', 'level_of_education',
                                   'q1', 'q2'])

        response_row = self._create_response_row()
        self.assertEqual(rows[2], response_row)

    def tearDown(self):
        self._rm_tree()
