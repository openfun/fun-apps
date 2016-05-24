import unittest

from fun_instructor.instructor_task_api.submit_tasks import submit_generate_answers_distribution_report
from fun.tests.utils import skipUnlessLms


@unittest.skip("Skip this test until we have adequately split our apps in lms/cms/common categories")
@skipUnlessLms
class FunInstructorTaskCourseSubmitTest(unittest.TestCase):

    def test_submit_generate_answers_distribution_report(self):
        api_call = lambda: submit_generate_answers_distribution_report(
            self.create_task_request(self.instructor),
            self.course.id,
            task_input={}
        )
        self._test_resubmission(api_call)
