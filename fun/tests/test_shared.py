import os
import shutil

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import TEST_DATA_MOCK_MODULESTORE

from fun import shared

@override_settings(SHARED_ROOT='/tmp/shared-test', MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class SharedTestCase(TestCase):

    def setUp(self):
        if os.path.exists(settings.SHARED_ROOT):
            shutil.rmtree(settings.SHARED_ROOT)

    def test_shared_directory_is_created(self):
        shared.ensure_directory_exists("subdir")
        self.assertTrue(os.path.isdir(settings.SHARED_ROOT))
        self.assertTrue(os.path.isdir(os.path.join(settings.SHARED_ROOT, "subdir")))

    @override_settings(ENVIRONMENT='prod')
    def test_shared_directory_is_not_created(self):
        self.assertRaises(ValueError, shared.ensure_root_exists)

    def test_tempfile(self):
        temp1 = shared.NamedTemporaryFile()
        temp2 = shared.NamedTemporaryFile(dir="temp2")

        self.assertTrue(temp1.name.startswith(settings.SHARED_ROOT))
        self.assertTrue(temp2.name.startswith(
            os.path.join(settings.SHARED_ROOT, "temp2")
        ))

    def test_get_safe_path(self):
        path = shared.get_safe_path("dir1", "dir2", "myfile")
        self.assertTrue(os.path.isdir(settings.SHARED_ROOT + "/dir1/dir2"))

    def test_get_course_path(self):
        course = CourseFactory.create()
        course_path = shared.get_course_path("answers_distribution_reports",
                                             course, "exo1.csv")
        self.assertTrue(os.path.exists(os.path.dirname(course_path)))
        self.assertEqual("exo1.csv", os.path.basename(course_path))
