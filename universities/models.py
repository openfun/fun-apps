from django.db import models
from django.utils.translation import ugettext as _

from ckeditor.fields import RichTextField


class University(models.Model):
    """
    A university or a school that provides online courses.
    """
    name = models.CharField(_('name'), max_length=255)
    code = models.CharField(_('code'), max_length=255, unique=True)
    certificate_logo = models.ImageField(_('certificate logo'),
        upload_to='universities', null=True, blank=True,
        help_text=_('Logo to be displayed on the certificate document.'))
    logo = models.ImageField(_('logo'), upload_to='universities')
    featured = models.BooleanField(_('featured on site'), default=False,
        help_text=_('Shows the logo on various sections of the site and enables '
        'the university page.'))
    slug = models.SlugField(_('slug'), max_length=255, unique=True, blank=True,
        help_text=_('Only used is set as featured'))
    banner = models.ImageField(_('banner'), upload_to='universities', null=True,
        blank=True)
    description = RichTextField(_('description'), blank=True)
    dm_user_id = models.CharField(_('DM User ID'), max_length=255, blank=True)
    dm_api_key = models.CharField(_('DM API Key'), max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ('order', 'id',)
        verbose_name = _('University')
        verbose_name_plural = _('Universities')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('universities-detail', (self.slug,))
