# -*- coding: utf-8 -*-

import ckeditor.fields

from django.conf import settings
from django.core.validators import validate_slug
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language



class ArticleManager(models.Manager):

    FEATURED_ARTICLES_COUNT = 14

    def published(self):
        """
        Return the queryset that corresponds to all published articles.
        """
        return self.filter(published=True)

    def published_or(self, **kwargs):
        """
        Return a queryset that corresponds to all published articles or a set
        of constraints.
        """
        return self.filter(models.Q(published=True) | models.Q(**kwargs))

    def viewable(self, language=None):
        """
        Return a queryset of all published articles in the specified language.
        """
        results = self.published()
        if language is not None:
            results = results.filter(language=language)
        return results

    def featured(self):
        """
        Return the first FEATURED_ARTICLES_COUNT articles in the current user's
        language.
        """
        return self.viewable(get_language())[:ArticleManager.FEATURED_ARTICLES_COUNT]


class Article(models.Model):

    title = models.CharField(verbose_name=_("title"),
            max_length=256, blank=False)
    slug = models.SlugField(verbose_name=_("slug"),
            max_length=50, unique=True, blank=False, validators=[validate_slug])
    text = ckeditor.fields.RichTextField(verbose_name=_("text"),
            config_name='news', blank=True)
    language = models.CharField(verbose_name=_("language"),
            max_length=8, choices=settings.LANGUAGES, default='fr')
    created_at = models.DateTimeField(verbose_name=_("created at"),
            db_index=True)
    edited_at = models.DateTimeField(verbose_name=_("edited at"),
            auto_now=True)
    published = models.BooleanField(verbose_name=_("published"),
            default=False)

    objects = ArticleManager()

    class Meta:
        ordering = ["-created_at"]
