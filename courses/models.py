# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField

from . import choices as courses_choices


class Course(models.Model):
    key = models.CharField(max_length=200, verbose_name=_(u'Course key'),
        unique=True)
    university = models.ForeignKey('universities.University',
        related_name='+', null=True, blank=True)
    subjects = models.ManyToManyField('CourseSubject', related_name='courses',
        null=True, blank=True)
    level = models.CharField(_('level'), max_length=255,
        choices=courses_choices.COURSE_LEVEL_CHOICES)

    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def __unicode__(self):
        return _('Course {}').format(self.key)


class CourseSubject(models.Model):
    name = models.CharField(_('name'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    description = RichTextField(_('description'), blank=True)
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        ordering = ('order', 'id',)
        verbose_name = _('Course Subject')
        verbose_name_plural = _('Course Subjects')

    def __unicode__(self):
        return self.name
