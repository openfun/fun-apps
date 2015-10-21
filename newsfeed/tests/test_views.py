# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import TestCase

from django.core.urlresolvers import reverse

from student.tests.factories import UserFactory

from fun.tests.utils import skipUnlessLms
from . import factories


@skipUnlessLms
class ViewArticlesTest(TestCase):

    def create_user_and_login(self, as_staff=False):
        user = UserFactory(is_staff=as_staff)
        self.client.login(username=user.username, password='test')

    def test_empty_article_list(self):
        url = reverse("newsfeed-landing")
        self.client.get(url)

    def test_article_list(self):
        published_article = factories.ArticleFactory.create(published=True)
        unpublished_article = factories.ArticleFactory.create(title="Work in progress", slug="work-in-progress",
                published=False)

        url = reverse("newsfeed-landing")
        response = self.client.get(url)

        self.assertIn(str(published_article.title), response.content)
        self.assertNotIn(str(unpublished_article.title), response.content)

    def test_article_details(self):
        article = factories.ArticleFactory.create(title="great title", published=True)

        url = reverse("newsfeed-article", kwargs={"slug": article.slug})
        response = self.client.get(url)

        self.assertIn(str(article.title), response.content)

    def test_preview_without_rights(self):
        self.create_user_and_login(False)
        self.preview_article(404)

    def test_preview_with_rights(self):
        self.create_user_and_login(True)
        self.preview_article(200)

    def preview_article(self, expected_status_code):
        article = factories.ArticleFactory.create(published=False)
        url = reverse('newsfeed-article-preview', kwargs={'slug': article.slug})
        response = self.client.get(url)
        self.assertEqual(expected_status_code, response.status_code)

    def test_preview_landing(self):
        self.create_user_and_login(True)
        article = factories.ArticleFactory.create(published=False, title="Unpublished article")
        featured_section = factories.FeaturedSectionFactory.create(article=article)
        url = reverse('newsfeed-landing-preview', kwargs={'slug': article.slug})
        response = self.client.get(url)

        self.assertTrue(str(article.slug) in response.content)
        self.assertTrue(str(featured_section.title) in response.content)

    def test_admin_upload_url(self):
        upload_url = reverse('news-ckeditor-upload')
        browse_url = reverse('news-ckeditor-browse')

        news_config = settings.CKEDITOR_CONFIGS['news']
        self.assertEqual(upload_url, news_config['filebrowserUploadUrl'])
        self.assertEqual(browse_url, news_config['filebrowserBrowseUrl'])
