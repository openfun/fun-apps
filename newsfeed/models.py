# -*- coding: utf-8 -*-

import ckeditor.fields

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.validators import validate_slug
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language

from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer


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


class ArticleCategory(models.Model):
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    order = models.PositiveIntegerField(_('order'), default=0)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('order', 'id')
        verbose_name = _('Article Category')
        verbose_name_plural = _('Article Categories')


class ArticleLink(models.Model):
    name = models.CharField(_('name'), max_length=255)
    url = models.CharField(_('url'), max_length=255)
    article = models.ForeignKey('Article', verbose_name=_('article'),
        related_name='links')

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Article Link')
        verbose_name_plural = _('Article Links')


class Article(models.Model):
    title = models.CharField(verbose_name=_("title"),
            max_length=256, blank=False)
    slug = models.SlugField(verbose_name=_("slug"),
            max_length=50, unique=True, blank=False, validators=[validate_slug])
    category = models.ForeignKey('ArticleCategory', verbose_name=_('category'),
        null=True, blank=True, related_name='articles')
    courses = models.ManyToManyField('courses.Course', verbose_name=_('courses'),
        related_name='articles', limit_choices_to={'is_active': True}, blank=True)
    thumbnail = models.ImageField(_('thumbnail'),
        upload_to='newsfeed', null=True, blank=True,
        help_text=_('Displayed on the news list page.'))
    lead_paragraph = models.CharField(verbose_name=_("Lead paragraph"),
            max_length=256, blank=True)
    text = ckeditor.fields.RichTextField(verbose_name=_("text"),
            config_name='default', blank=True)
    event_date = models.DateTimeField(verbose_name=_("event date"),
        null=True, blank=True)
    language = models.CharField(verbose_name=_("language"),
            max_length=8, choices=settings.LANGUAGES, default='fr')
    created_at = models.DateTimeField(verbose_name=_("created at"),
            db_index=True, default=timezone.now)
    edited_at = models.DateTimeField(verbose_name=_("edited at"),
            auto_now=True)
    published = models.BooleanField(verbose_name=_("published"),
            default=False)

    microsite = models.CharField(max_length=128, blank=True, db_index=True)

    objects = ArticleManager()

    class Meta:
        ordering = ["-created_at"]

    def related(self):
        """
        Return article that share the same category.
        """
        queryset = Article.objects.published()
        queryset = queryset.filter(category=self.category)
        return queryset

    def __unicode__(self):
        return self.title

    def get_lead_paragraph(self):
        return self.lead_paragraph if self.lead_paragraph else ''

    def get_thumbnail(self, size):
        try:
            thumbnailer = get_thumbnailer(self.thumbnail)
            # The thumbnail sizes were defined to have the same ratio in
            # all formats: width/height = 1.648
            sizes = {
                'very-big': (1030, 625),
                'big': (570, 346),
                'primary': (570, 346),
                'secondary': (275, 167),
                'facebook': (600, 364)
            }
            thumbnail_options = {'crop': 'smart', 'size': sizes[size], 'upscale': True}
            return thumbnailer.get_thumbnail(thumbnail_options)
        except InvalidImageFormatError:
            return ''  ## todo: generic image

    def get_absolute_url(self):
        return reverse('newsfeed-article', args=[self.slug])
