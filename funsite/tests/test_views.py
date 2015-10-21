import random

from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms
import newsfeed.tests.factories as newsfactories


@skipUnlessLms
class TestHomepage(TestCase):

    def setUp(self):
        random.seed(0)

    def get_root_page(self):
        return self.client.get(reverse("root"))

    def test_no_course(self):
        self.get_root_page()

    def test_with_news(self):
        category = newsfactories.ArticleCategoryFactory.create()
        newsfactories.ArticleFactory.create(category=category)
        newsfactories.ArticleFactory.create(category=category)
        newsfactories.ArticleFactory.create(category=category)

        self.get_root_page()
