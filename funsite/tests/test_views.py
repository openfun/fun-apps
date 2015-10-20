import random

from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms
import newsfeed.tests.factories as newsfactories


@skipUnlessLms
class TestHomepage(TestCase):

    ROOT_PAGE_NUM_QUERIES = 7

    def setUp(self):
        random.seed(0)

    def get_root_page(self):
        return self.client.get(reverse("root"))

    def test_no_course(self):
        with self.assertNumQueries(self.ROOT_PAGE_NUM_QUERIES):
            self.get_root_page()

    def test_news_do_not_require_additional_queries(self):
        category = newsfactories.ArticleCategoryFactory.create()
        newsfactories.ArticleFactory.create(category=category)
        newsfactories.ArticleFactory.create(category=category)
        newsfactories.ArticleFactory.create(category=category)

        with self.assertNumQueries(self.ROOT_PAGE_NUM_QUERIES):
            self.get_root_page()
