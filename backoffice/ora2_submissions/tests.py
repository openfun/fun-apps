import os
import celery.states

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from instructor_task.tests.factories import InstructorTaskFactory

from backoffice.ora2_submissions import tasks_api, tasks
from backoffice.tests.test import BaseBackoffice
from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class TestDownloadOra2Submissions(BaseBackoffice):

    def setUp(self):
        super(TestDownloadOra2Submissions, self).setUp()
        self.login_with_backoffice_group()
        self.status_url = reverse("backoffice:ora2-submissions:status",
                args=[self.course.id.to_deprecated_string()])
        self.prepare_url = reverse("backoffice:ora2-submissions:prepare",
                args=[self.course.id.to_deprecated_string()])
        self.download_url = reverse("backoffice:ora2-submissions:download",
                args=[self.course.id.to_deprecated_string()])

    def test_unauthorized_user_has_no_access(self):
        self.client.logout()
        response = self.client.get(self.download_url)

        self.assertEqual(302, response.status_code)

    def test_get_output_path(self):
        from collections import namedtuple
        task = namedtuple("MockInstructorTask", ['task_output'])(None)
        self.assertIsNone(tasks.get_output_path(task))

    def test_download_file_without_preparation(self):
        is_prepared = tasks_api.file_is_prepared(self.course.id)
        last_file_date = tasks_api.get_last_file_date(self.course.id)
        response = self.client.get(self.download_url)

        self.assertFalse(is_prepared)
        self.assertIsNone(last_file_date)
        self.assertEqual(404, response.status_code)

    def test_download_file(self):
        self.login_with_backoffice_group()
        response_prepare = self.client.post(self.prepare_url, follow=True)
        instructor_task = tasks.InstructorTask.objects.get()
        is_prepared = tasks_api.file_is_prepared(self.course.id)
        file_path = tasks_api.get_file_path(self.course.id)
        response = self.client.get(self.download_url)

        self.assertEqual("SUCCESS", instructor_task.task_state)
        self.assertTrue(is_prepared)
        self.assertIsNotNone(file_path)
        self.assertTrue(os.path.exists(file_path))
        self.assertTrue(response_prepare.redirect_chain[0][0].endswith(self.status_url))
        self.assertEqual(200, response.status_code)
        self.assertEqual('application/x-gzip', response['Content-Type'])
        self.assertNotEqual('', response.content)

    def test_prepare_fails_on_GET(self):
        response = self.client.get(self.prepare_url)
        self.assertEqual(405, response.status_code)

    def test_prepare_file_twice(self):
        # Prepare 1st file
        self.client.post(self.prepare_url)
        file_path1 = tasks_api.get_file_path(self.course.id)
        last_file_date1 = tasks_api.get_last_file_date(self.course.id)
        self.assertTrue(os.path.exists(file_path1))

        # Prepare 2nd file
        self.client.post(self.prepare_url)
        file_path2 = tasks_api.get_file_path(self.course.id)
        last_file_date2 = tasks_api.get_last_file_date(self.course.id)
        self.assertFalse(os.path.exists(file_path1))
        self.assertTrue(os.path.exists(file_path2))
        self.assertLess(last_file_date1, last_file_date2)

    def test_status_view(self):
        response = self.client.get(self.status_url)
        self.assertEqual(200, response.status_code)

    @override_settings(TEMPLATE_STRING_IS_INVALID="__INVALID__")
    def test_status_view_with_running_task(self):
        InstructorTaskFactory(
            task_key=tasks_api.get_task_key(self.course.id),
            course_id=self.course.id,
            task_id="task_id",
            task_type=tasks.PREPARATION_TASK_TYPE,
        )
        response = self.client.get(self.status_url)
        self.assertTrue("task_is_running" in response.context)
        self.assertTrue(response.context["task_is_running"])
        self.assertFalse("__INVALID__" in response.content)

    def test_last_successful_tasks_have_valid_task_output(self):
        InstructorTaskFactory(
            task_key=tasks_api.get_task_key(self.course.id),
            course_id=self.course.id,
            task_id="task_id",
            task_type=tasks.PREPARATION_TASK_TYPE,
            task_output=None,
            task_state=celery.states.SUCCESS,
        )
        last_successful_task = tasks_api.get_last_successful_instructor_task(self.course.id)
        self.assertIsNone(last_successful_task)
