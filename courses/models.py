# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField

from courseware.courses import get_course, get_course_about_section
from opaque_keys.edx.locator import CourseLocator
from xmodule.contentstore.content import StaticContent

from . import choices as courses_choices
from .managers import CourseSubjectManager


class Course(models.Model):
    key = models.CharField(max_length=200, verbose_name=_(u'Course key'),
        unique=True)
    universities = models.ManyToManyField('universities.University',
        through='CourseUniversityRelation', related_name='courses')
    subjects = models.ManyToManyField('CourseSubject', related_name='courses',
        null=True, blank=True)
    level = models.CharField(_('level'), max_length=255,
        choices=courses_choices.COURSE_LEVEL_CHOICES, blank=True)
    score = models.PositiveIntegerField(_('score'), default=0, db_index=True)

    class Meta:
        ordering = ('-score',)
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    @property
    def course_locator(self):
        return CourseLocator.from_string(self.key)

    @property
    def course_descriptor(self):
        try:
            course = get_course(self.course_locator)
        except ValueError:
            course = None
        return course

    @property
    def image_url(self):
        if not self.course_descriptor:
            return ''
        location = StaticContent.compute_location(
            self.course_locator, self.course_descriptor.course_image
        )
        return location.to_deprecated_string()

    @property
    def title(self):
        if not self.course_descriptor:
            return ''
        title = get_course_about_section(self.course_descriptor, 'title')
        return title

    @property
    def short_description(self):
        if not self.course_descriptor:
            return ''
        description = get_course_about_section(
            self.course_descriptor, 'short_description'
        )
        return description

    def __unicode__(self):
        return _('Course {}').format(self.key)


class CourseSubject(models.Model):
    name = models.CharField(_('name'), max_length=255, db_index=True)
    short_name = models.CharField(_('short name'), max_length=255, blank=True,
        help_text=_('Displayed where space is rare - on side panel for instance.'))
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    description = RichTextField(_('description'), blank=True)
    featured = models.BooleanField(verbose_name=_('featured'))
    image = models.ImageField(_("image"), upload_to="courses",
        null=True, blank=True)
    score = models.PositiveIntegerField(_('score'), default=0, db_index=True)

    objects = CourseSubjectManager()

    class Meta:
        ordering = ('-score', 'name', 'id',)
        verbose_name = _('Course Subject')
        verbose_name_plural = _('Course Subjects')

    def get_absolute_url(self):
        return '/TODO/'

    def __unicode__(self):
        return self.name


class CourseUniversityRelation(models.Model):
    university = models.ForeignKey('universities.University',
        related_name='related_courses')
    course = models.ForeignKey('Course',
        related_name='related_universities')
    order = models.PositiveIntegerField(_('order'), default=0, db_index=True)

    class Meta:
        ordering = ('order', 'id',)
        verbose_name = _('course-university relation')
        verbose_name_plural = _('course-university relation')

    def __unicode__(self):
        return u'{} - {}'.format(self.university, self.course)
