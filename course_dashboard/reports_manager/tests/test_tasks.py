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

    def test_generate_answers_distribution_report(self):
        cmap = self._build_correct_map('correct')
        student_answers = self._build_student_answers(OPTION_1, OPTION_2)
        student_name = 'joe'

        StudentModuleFactory(course_id=self.course.id,
                             module_state_key=self.problem_module.location,
                             student=UserFactory(username=student_name,
                                                 profile__year_of_birth=u'1989',
                                                 profile__level_of_education=u'bac'),
                             state=self._build_student_module_state(cmap, student_answers))
        
        running_report_name = build_answers_distribution_report_name(self.problem_module)
        task_input = {'problem_id' : self.problem_module.location.name,
                      'running_report_name' : running_report_name}

        with patch('instructor_task.tasks_helper._get_current_task'):
            result = generate_answers_distribution_report(None, self.course.id,
                                                          task_input, None)
        rows = self._read_report_file(get_path(task_input['running_report_name'],
                                               self.problem_module.location))

        self.assertEqual(rows[1], ['id', 'gender', 'year_of_birth', 'level_of_education',
                                   'q1', 'q2'])

        user = User.objects.get(username='joe')
        user_profile = UserProfile.objects.get(user=user)
        real_row = [unicode(user.id), unicode(user_profile.gender),
                    unicode(user_profile.year_of_birth), unicode(user_profile.level_of_education)]

        real_row.extend([OPTION_1, OPTION_2])
        self.assertEqual(rows[2], real_row)

    def _read_report_file(self, filepath):
        with codecs.open(filepath, 'r', 'utf-8') as report:
            reader = unicodecsv.reader(report, encoding='utf-8')
            rows = list(reader)
        return rows

    def tearDown(self):
        if os.path.exists(settings.SHARED_ROOT):
            shutil.rmtree(settings.SHARED_ROOT)
