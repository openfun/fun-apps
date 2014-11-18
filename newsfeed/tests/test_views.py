# -*- coding: utf-8 -*-
from django.test import TestCase

from django.core.urlresolvers import reverse

from student.tests.factories import UserFactory

from .factories import ArticleFactory


class ViewArticlesTest(TestCase):

    def test_article_list(self):
        published_article = ArticleFactory.create(published=True)
        unpublished_article = ArticleFactory.create(title="Work in progress", slug="work-in-progress",
                published=False)

        url = reverse("newsfeed-landing")
        response = self.client.get(url)

        self.assertIn(str(published_article.title), response.content)
        self.assertNotIn(str(unpublished_article.title), response.content)

    def test_article_details(self):
        article = ArticleFactory.create(title="great title", published=True)

        url = reverse("newsfeed-article", kwargs={"slug": article.slug})
        response = self.client.get(url)

        self.assertIn(str(article.title), response.content)

    def test_preview_without_rights(self):
        user = UserFactory(is_staff=False)
        self.client.login(username=user.username, password='test')

        self.preview_article(404)

    def test_preview_with_rights(self):
        user = UserFactory(is_staff=True)
        self.client.login(username=user.username, password='test')

        self.preview_article(200)

    def preview_article(self, expected_status_code):
        article = ArticleFactory.create(published=False)
        url = reverse('newsfeed-article-preview', kwargs={'slug': article.slug})
        response = self.client.get(url)
        self.assertEqual(expected_status_code, response.status_code)

    def test_preview_landing(self):
        article = ArticleFactory.create(published=False)
        url = reverse('newsfeed-landing-preview', kwargs={'slug': article.slug})
        response = self.client.get(url)
        #self.assertIn(str(article.title), response.content)# TODO
