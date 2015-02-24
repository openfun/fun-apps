import os

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

import shutil

from fun import shared

@override_settings(SHARED_ROOT='/tmp/shared-test')
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
