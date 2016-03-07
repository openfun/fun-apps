# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, ModelChoiceField

from ckeditor.fields import RichTextField


class Teacher(models.Model):
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    full_name = models.CharField(max_length=300, verbose_name=_("Full name"))
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    profile_image = models.ImageField(_('profile image'), upload_to='teachers',
        null=True, blank=True)
    bio = RichTextField(_('bio'), blank=True)

    class Meta:
        verbose_name = _('teacher')
        verbose_name_plural = _('teachers')

    def __unicode__(self):
        return self.full_name


class CourseTeacherRelation(models.Model):
    course = models.ForeignKey('courses.Course', related_name='%(class)s_related')
    teacher = models.ForeignKey('Teacher', related_name='+')
    order = models.PositiveIntegerField(_('order'), default=0)

    class Meta:
        abstract = True
        ordering = ('order', 'id',)
        unique_together = ('course', 'teacher')

    def __unicode__(self):
        return u'{} - {}'.format(self.course, self.teacher)


class CourseTeacher(CourseTeacherRelation):
    '''
    A teacher that is displayed on a course page.
    '''

    class Meta(CourseTeacherRelation.Meta):
        verbose_name = _('course teacher')
        verbose_name_plural = _('course teachers')


class CertificateTeacher(CourseTeacherRelation):
    '''
    A teacher that is displayed on the certificate.
    '''

    class Meta(CourseTeacherRelation.Meta):
        verbose_name = _('certificate teacher')
        verbose_name_plural = _('certificate teachers')
