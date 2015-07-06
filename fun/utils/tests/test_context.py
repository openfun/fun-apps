import os

from django.test import TestCase

from fun.utils.context import setenv

class TestSetEnv(TestCase):

    def setUp(self):
        if "dummyvalue" in os.environ:
            del os.environ["dummyvalue"]

    def test_undefined_value_remains_undefined(self):
        self.assertFalse("dummyvalue" in os.environ)
        with setenv("dummyvalue", "val"):
            self.assertEqual("val", os.environ["dummyvalue"])
        self.assertFalse("dummyvalue" in os.environ)

    def test_unset_undefined_value(self):
        with setenv("dummyvalue", None) as context:
            self.assertIsNone(context.saved_value)
            self.assertFalse("dummyvalue" in os.environ)
        self.assertFalse("dummyvalue" in os.environ)

    def test_undefine_value(self):
        os.environ["dummyvalue"] = "oldvalue"
        with setenv("dummyvalue", None):
            self.assertFalse("dummyvalue" in os.environ)
        self.assertEqual("oldvalue", os.environ["dummyvalue"])
