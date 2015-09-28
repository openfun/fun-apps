import random

from django.test import TestCase

from fun.tests.utils import skipUnlessLms


class TestHomepage(TestCase):

    def setUp(self):
        random.seed(0)

    def test_no_course(self):
        self.client.get("")
