# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.exceptions import InvalidImageFormatError
from ckeditor.fields import RichTextField

from .managers import UniversityManager


class University(models.Model):
    """
    A university or a school that provides online courses.
    """
    name = models.CharField(_('name'), max_length=255, db_index=True)
    short_name = models.CharField(_('short name'), max_length=255, blank=True,
        help_text=_('Displayed where space is rare - on side panel for instance.'))
    code = models.CharField(_('code'), max_length=255, unique=True)
    certificate_logo = models.ImageField(_('certificate logo'),
        upload_to='universities', null=True, blank=True,
        help_text=_('Logo to be displayed on the certificate document.'))
    logo = models.ImageField(_('logo'), upload_to='universities')
    detail_page_enabled = models.BooleanField(_('detail page enabled'),
        default=False, db_index=True,
        help_text=_('Enables the university detail page.'))
    is_obsolete = models.BooleanField(_('is obsolete'),
        default=False, db_index=True,
        help_text=_('Obsolete universities are not displayed on the site.'))
    slug = models.SlugField(_('slug'), max_length=255, unique=True, blank=True,
        help_text=_('Only used if detail page is enabled'))
    banner = models.ImageField(_('banner'), upload_to='universities', null=True,
        blank=True)
    description = RichTextField(_('description'), blank=True)
    dm_user_id = models.CharField(_('DM User ID'), max_length=255, blank=True)
    dm_api_key = models.CharField(_('DM API Key'), max_length=255, blank=True)
    score = models.PositiveIntegerField(_('score'), default=0, db_index=True)

    objects = UniversityManager()

    class Meta:
        ordering = ('-score', 'id',)
        verbose_name = _('University')
        verbose_name_plural = pgettext('University model', 'Universities')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        if self.slug:
            return ('universities-detail', (self.slug,))

    def get_banner(self):
        options = {'size': (1030, 410), }
        try:
            thumbnail = get_thumbnailer(self.banner).get_thumbnail(options)
            return thumbnail.url
        except InvalidImageFormatError:
            return '' # we could return a nice grey image

    def get_short_name(self):
        return self.short_name or self.name

    def get_logo_thumbnail(self):
        options = {'size': (180, 100), }
        try:
            thumbnail = get_thumbnailer(self.logo).get_thumbnail(options)
            return thumbnail.url
        except InvalidImageFormatError:
            return '' # we could return a nice grey image

