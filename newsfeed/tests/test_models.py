# -*- coding: utf-8 -*-
from django.db import IntegrityError
from django.test import TestCase
import django.utils.translation

from newsfeed import models

from .factories import ArticleFactory


class ArticleTest(TestCase):

    def test_create(self):
        article = ArticleFactory.create()

        self.assertEqual('fr', article.language)
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.edited_at)
        self.assertFalse(article.published)

    def test_create_with_identical_slugs(self):
        article = ArticleFactory.create()
        self.assertRaises(IntegrityError,
                ArticleFactory.create,
                title="title 2", text="text 2", slug=article.slug)

    def test_ordering(self):
        article1 = ArticleFactory.create()
        article2 = ArticleFactory.create()

        self.assertLess(article1.created_at, article2.created_at)
        articles = models.Article.objects.all()
        self.assertEqual(article2.pk, articles[0].pk)
        self.assertEqual(article1.pk, articles[1].pk)

    def test_featured_articles(self):
        django.utils.translation.activate("en")
        count1 = len(models.Article.objects.featured())
        ArticleFactory.create(published=False)
        count2 = len(models.Article.objects.featured())
        ArticleFactory.create(published=True, language="fr")
        count3 = len(models.Article.objects.featured())
        ArticleFactory.create(published=True, language="en")
        count4 = len(models.Article.objects.featured())

        self.assertEqual(0, count1)
        self.assertEqual(0, count2)
        self.assertEqual(0, count3)
        self.assertEqual(1, count4)

    def test_viewable_articles(self):
        french_article = ArticleFactory.create(title=u"Un article en français",
                language="fr", published=True)
        english_article = ArticleFactory.create(title=u"An article in English",
                language="en", published=True)

        #django.utils.translation.activate("en")
        articles = models.Article.objects.viewable('en')
        self.assertEqual(1, len(articles))
        self.assertEqual(english_article.pk, articles[0].pk)

        #django.utils.translation.activate("fr")
        articles = models.Article.objects.viewable('fr')
        self.assertEqual(1, len(articles))
        self.assertEqual(french_article.pk, articles[0].pk)

    def test_published_or(self):
        article1 = ArticleFactory.create(published=False)
        article2 = ArticleFactory.create(published=True)
        ArticleFactory.create(published=False)

        articles = models.Article.objects.published_or(pk=article1.pk)
        self.assertEqual(2, len(articles))
        self.assertEqual(article2.pk, articles[0].pk)
        self.assertEqual(article1.pk, articles[1].pk)
