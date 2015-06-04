import os

from django.test import TestCase

from fun.utils.context import setenv

class TestSetEnv(TestCase):

    def setUp(self):
        if "POUAC" in os.environ:
            del os.environ["POUAC"]

    def test_undefined_value_remains_undefined(self):
        self.assertFalse("POUAC" in os.environ)
        with setenv("POUAC", "val"):
            self.assertEqual("val", os.environ["POUAC"])
        self.assertFalse("POUAC" in os.environ)

    def test_unset_undefined_value(self):
        with setenv("POUAC", None) as context:
            self.assertIsNone(context.saved_value)
            self.assertFalse("POUAC" in os.environ)
        self.assertFalse("POUAC" in os.environ)

    def test_undefine_value(self):
        os.environ["POUAC"] = "oldvalue"
        with setenv("POUAC", None):
            self.assertFalse("POUAC" in os.environ)
        self.assertEqual("oldvalue", os.environ["POUAC"])
