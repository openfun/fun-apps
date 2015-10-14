# -*- coding: utf-8 -*-

import ckeditor.fields

from django.conf import settings
from django.core.validators import validate_slug
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language

from solo.models import SingletonModel


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


class FeaturedSection(SingletonModel):

    article = models.ForeignKey("Article", verbose_name=_("article"),
        blank=True, null=True, related_name="a_+")
    title = models.CharField(verbose_name=_("title"), max_length=256,
        blank=True, help_text=_("If no title is given here, we will use "
        "the related article's title."))
    image = models.ImageField(_("image"),
        upload_to="newsfeed", help_text=_("Featured on the top section of "
        "the page."))

    def __unicode__(self):
        return u"FeaturedSection"

    class Meta:
        verbose_name = _("Featured Section")
        verbose_name_plural = _("Featured Section")


class Article(models.Model):

    title = models.CharField(verbose_name=_("title"),
            max_length=256, blank=False)
    slug = models.SlugField(verbose_name=_("slug"),
            max_length=50, unique=True, blank=False, validators=[validate_slug])
    thumbnail = models.ImageField(_('thumnail'),
        upload_to='newsfeed', null=True, blank=True,
        help_text=_('Displayed on the news list page.'))
    lead_paragraph = models.CharField(verbose_name=_("Lead paragraph"),
            max_length=256, blank=True)
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
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    microsite = models.CharField(max_length=128, blank=True, db_index=True)

    objects = ArticleManager()

    class Meta:
        ordering = ["order", "-created_at"]

    def __unicode__(self):
        return self.title

    def get_lead_paragraph(self):
        LEADING_WORDS = 30
        if self.lead_paragraph:
            return self.lead_paragraph
        else:
            lead_paragraph = ' '.join(self.text.split(' ')[:LEADING_WORDS])
            return lead_paragraph