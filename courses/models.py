# -*- coding: utf-8 -*-
import random

from django.db import models
from django.utils.translation import ugettext_lazy as _

from ckeditor.fields import RichTextField

from courseware.courses import get_course, get_course_about_section
from opaque_keys.edx.locator import CourseLocator
from xmodule.contentstore.content import StaticContent

from . import choices as courses_choices
from .managers import CourseSubjectManager, CourseManager


course_subject_images_mapping = {
    'philosophie': 'brain.png',
    'economie-et-finance': 'money.png',
    'physique': 'physique.png',
    'informatique-programmation': 'screen.png',
    'droit': 'justice.png',
    'education-formation': 'teacher.png',
    'environnement-developpement-durable': 'earth.png',
    'langues': 'bubbles.png',
    'management-entrepreunariat': 'building.png',
    'sante': 'caduce.png',
    'sciences-humaines-et-sociales': 'book.png',
    'sciences': 'microscope.png',
}

class Course(models.Model):
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)
    key = models.CharField(max_length=200, verbose_name=_(u'Course key'),
        unique=True)
    title = models.CharField(_(u'title'), max_length=255, blank=True)
    short_description = models.TextField(_('short description'), blank=True)
    image_url = models.CharField(_(u'image url'), max_length=255, blank=True)
    universities = models.ManyToManyField('universities.University',
        through='CourseUniversityRelation', related_name='courses')
    subjects = models.ManyToManyField('CourseSubject', related_name='courses',
        null=True, blank=True)
    level = models.CharField(_('level'), max_length=255,
        choices=courses_choices.COURSE_LEVEL_CHOICES, blank=True, db_index=True)
    is_active = models.BooleanField(verbose_name=_('is active'), default=False)
    prevent_auto_update = models.BooleanField(
        verbose_name=_('prevent automatic update'), default=False)
    session_number = models.PositiveIntegerField(_('session'), default=1)
    score = models.PositiveIntegerField(_('score'), default=0, db_index=True)
    start_date = models.DateTimeField(verbose_name=_('start date'), db_index=True,
        null=True, blank=True)
    end_date = models.DateTimeField(verbose_name=_('end date'), db_index=True,
        null=True, blank=True)

    objects = CourseManager()

    class Meta:
        ordering = ('-score',)
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    @staticmethod
    def random_featured(limit_to=7):
        courses = Course.objects.by_score()[:limit_to]
        courses = list(courses)
        random.shuffle(courses)
        return courses

    @property
    def session_display(self):
        display_text = ''
        if self.session_number > 1:
            display_text = _('session {}'.format(self.session_number))
        return display_text

    def __unicode__(self):
        return _('Course {}').format(self.key)


class CourseSubject(models.Model):
    name = models.CharField(_('name'), max_length=255, db_index=True)
    short_name = models.CharField(_('short name'), max_length=255, blank=True,
        help_text=_('Displayed where space is rare - on side panel for instance.'))
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    description = RichTextField(_('description'), blank=True)
    featured = models.BooleanField(verbose_name=_('featured'), db_index=True)
    image = models.ImageField(_("image"), upload_to="courses",
        null=True, blank=True)
    score = models.PositiveIntegerField(_('score'), default=0, db_index=True)

    objects = CourseSubjectManager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('-score', 'name', 'id',)
        verbose_name = _('Course Subject')
        verbose_name_plural = _('Course Subjects')

    def get_absolute_url(self):
        return '/TODO/'

    def get_image_url(self):
        if self.featured:
            if self.image:
                return self.image.url
            else:
                try:
                    return '/static/funsite/images/icones/themes/%s' % course_subject_images_mapping[self.slug]
                except KeyError:
                    return ''


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
