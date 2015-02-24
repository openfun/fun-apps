import os

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from xmodule.modulestore.tests.django_utils import TEST_DATA_MOCK_MODULESTORE

from backoffice.ora2_submissions import tasks as ora2_submission_tasks
from backoffice.tests.test import BaseBackoffice


@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
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

    def test_download_file_without_preparation(self):
        is_prepared = ora2_submission_tasks.file_is_prepared(self.course.id)
        last_file_date = ora2_submission_tasks.get_last_file_date(self.course.id)
        response = self.client.get(self.download_url)

        self.assertFalse(is_prepared)
        self.assertIsNone(last_file_date)
        self.assertEqual(404, response.status_code)

    def test_download_file(self):
        self.login_with_backoffice_group()
        response_prepare = self.client.post(self.prepare_url, follow=True)
        is_prepared = ora2_submission_tasks.file_is_prepared(self.course.id)
        file_path = ora2_submission_tasks.get_file_path(self.course.id)
        response = self.client.get(self.download_url)

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
        file_path1 = ora2_submission_tasks.get_file_path(self.course.id)
        last_file_date1 = ora2_submission_tasks.get_last_file_date(self.course.id)
        self.assertTrue(os.path.exists(file_path1))

        # Prepare 2nd file
        self.client.post(self.prepare_url)
        file_path2 = ora2_submission_tasks.get_file_path(self.course.id)
        last_file_date2 = ora2_submission_tasks.get_last_file_date(self.course.id)
        self.assertFalse(os.path.exists(file_path1))
        self.assertTrue(os.path.exists(file_path2))
        self.assertLess(last_file_date1, last_file_date2)

    def test_status_view(self):
        response = self.client.get(self.status_url)
        self.assertEqual(200, response.status_code)
