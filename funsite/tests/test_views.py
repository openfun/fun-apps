import random

from django.core.urlresolvers import reverse
from django.test import TestCase

from backoffice.tests.test_microsites import FAKE_MICROSITE1, FAKE_MICROSITE2
from fun.tests.utils import skipUnlessLms, setMicrositeTestSettings
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

    def test_unpublished_news_are_not_displayed(self):
        article = newsfactories.ArticleFactory.create(published=False)
        response = self.get_root_page()
        self.assertFalse(str(article.title) in response.content)

    @setMicrositeTestSettings(FAKE_MICROSITE2)
    def test_news_from_different_microsite_are_not_displayed(self):
        article = newsfactories.ArticleFactory.create(
            microsite=FAKE_MICROSITE1["SITE_NAME"],
            published=True
        )
        response = self.get_root_page()
        self.assertFalse(str(article.title) in response.content)
