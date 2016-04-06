# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import TestCase

from django.core.urlresolvers import reverse

from student.tests.factories import UserFactory

from fun.tests.utils import skipUnlessLms
from . import factories


@skipUnlessLms
class ViewArticlesTest(TestCase):

    def setUp(self):
        from .. import views
        self.views = views

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
        content = response.content.decode("utf8")

        self.assertIn(unicode(published_article.title), content)
        self.assertNotIn(unicode(unpublished_article.title), content)

    def test_article_details(self):
        article = factories.ArticleFactory.create(title="great title", published=True)

        url = reverse("newsfeed-article", kwargs={"slug": article.slug})
        response = self.client.get(url)

        self.assertIn(unicode(article.title), response.content.decode("utf8"))

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
        url = reverse('newsfeed-landing-preview', kwargs={'slug': article.slug})
        response = self.client.get(url)
        content = response.content.decode("utf8")
        self.assertIn(unicode(article.slug), content)
        self.assertIn(unicode(article.title), content)

    def test_URL_parameters_parsing(self):
        d1 = {"p": "3.14", "n": "broken"}
        d2 = {"p": "2", "n":"3"}

        p1, n1 = self.views.parse_request(d1)
        p2, n2 = self.views.parse_request(d2)

        self.assertEqual(p1, 1)
        self.assertEqual(n1, self.views.ARTICLES_PER_PAGE)
        self.assertEqual(p2, 2)
        self.assertEqual(n2, 3)

    def test_pagination(self):
        """ we test that each page contains the right articles
        """
        # first article added is last one presented in news (older one)...
        articles = []
        for i in range(10):
            art = factories.ArticleFactory.create(published=True)
            articles.append(art)

        articles_per_page = 2

        #  we have 3 pages
        url = reverse("newsfeed-landing")
        responses = [self.client.get(url,
                        {"n": articles_per_page, "p": i})
                     for i in ("1", "2", "3")
                     ]
        contents = [r.content.decode("utf8") for r in responses]
        titles = [unicode(art.title) for art in articles]

        # we test that a page contains the right articles but also that it doesn't contain articles of other pages
        #  page 1
        self.assertIn(titles[-1], contents[0])
        self.assertIn(titles[-2], contents[0])
        self.assertIn(titles[-3], contents[0])
        self.assertNotIn(titles[6], contents[0])
        self.assertNotIn(titles[0], contents[0])

        # page 2
        self.assertIn(titles[-4], contents[1])
        self.assertIn(titles[-5], contents[1])
        self.assertNotIn(titles[0], contents[1])
        self.assertNotIn(titles[-1], contents[1])

        # page 3
        self.assertIn(titles[-6], contents[2])
        self.assertIn(titles[-7], contents[2])
        self.assertNotIn(titles[-1], contents[2])
        self.assertNotIn(titles[-4], contents[2])

    def test_pagination_boundaries(self):
        """ we test that each boundary condition returns the predefined page
        """
        articles = []
        for i in range(5):
            art = factories.ArticleFactory.create(title="Article {}".format(i), published=True)
            articles.append(art)

        articles_per_page = 2
        url = reverse("newsfeed-landing")

        responses = [self.client.get(url,
                        {"n": articles_per_page, "p": i})
                     for i in ("broken", "20", "0")
                     ]
        contents = [r.content.decode("utf8") for r in responses]
        titles = [unicode(art.title) for art in articles]

        self.assertIn(titles[4], contents[0])
        self.assertIn(titles[3], contents[0])
        self.assertIn(titles[2], contents[0])
        self.assertNotIn(titles[0], contents[0])
        self.assertNotIn(titles[1], contents[0])

        # empty page is last page
        self.assertIn(titles[0], contents[1])
        self.assertIn(titles[1], contents[1])

        #  empty page is last page
        self.assertIn(titles[0], contents[2])
        self.assertIn(titles[1], contents[2])
        self.assertNotIn(titles[2], contents[2])
        self.assertNotIn(titles[3], contents[2])
        self.assertNotIn(titles[4], contents[2])

    def test_sql_number_of_queries_in_paginate_for_page_1(self):
        qs = self.views.get_articles()
        with self.assertNumQueries(2) as qe:
            self.views.paginate(qs, 1, 10)

    def test_sql_number_of_queries_in_paginate_for_page_2(self):
        qs = self.views.get_articles()
        with self.assertNumQueries(1):
            self.views.paginate(qs, 2, 10)

    def test_admin_upload_url(self):
        upload_url = reverse('news-ckeditor-upload')
        browse_url = reverse('news-ckeditor-browse')

        news_config = settings.CKEDITOR_CONFIGS['news']
        self.assertEqual(upload_url, news_config['filebrowserUploadUrl'])
        self.assertEqual(browse_url, news_config['filebrowserBrowseUrl'])
