from instructor_task.tests.test_api import InstructorTaskCourseSubmitTest
from fun_instructor.instructor_task_api.submit_tasks import submit_generate_answers_distribution_report

class FunInstructorTaskCourseSubmitTest(InstructorTaskCourseSubmitTest):
    def test_submit_generate_answers_distribution_report(self):
        api_call = lambda: submit_generate_answers_distribution_report(
            self.create_task_request(self.instructor),
            self.course.id,
            task_input={}
        )
        self._test_resubmission(api_call)
