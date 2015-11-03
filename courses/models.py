# -*- coding: utf-8 -*-
from django.utils.timezone import now

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _

from ckeditor.fields import RichTextField
from jsonfield.fields import JSONField

from . import choices as courses_choices
from .managers import CourseSubjectManager, CourseManager


class Course(models.Model):
    modification_date = models.DateTimeField(_('modification date'), auto_now=True)
    key = models.CharField(max_length=200, verbose_name=_(u'Course key'),
        unique=True)
    title = models.CharField(_(u'title'), max_length=255, blank=True)
    university_display_name = models.CharField(_(u'university display name'),
        max_length=255, blank=True, help_text=_('Displayed in place of the '
        'university name. If not set, use the name of the first associated '
        'university.'))
    short_description = models.TextField(_('short description'), blank=True)
    image_url = models.CharField(_(u'image url'), max_length=255, blank=True)
    universities = models.ManyToManyField('universities.University',
        through='CourseUniversityRelation', related_name='courses')
    subjects = models.ManyToManyField('CourseSubject', related_name='courses',
        null=True, blank=True)
    level = models.CharField(_('level'), max_length=255,
        choices=courses_choices.COURSE_LEVEL_CHOICES, blank=True, db_index=True)
    show_in_catalog = models.BooleanField(verbose_name=_('show in catalog'),
        default=True, db_index=True, help_text=_('Controls whether a course is '
        'listed in the courses catalog page'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=False)
    prevent_auto_update = models.BooleanField(
        verbose_name=_('prevent automatic update'), default=False)
    session_number = models.PositiveIntegerField(_('session'), default=1,
        help_text=_("Set 0 if session doesn't make sense for this course."))
    score = models.PositiveIntegerField(_('score'), default=0, db_index=True)
    start_date = models.DateTimeField(verbose_name=_('start date'), db_index=True,
        null=True, blank=True)
    end_date = models.DateTimeField(verbose_name=_('end date'), db_index=True,
        null=True, blank=True)
    enrollment_start_date = models.DateTimeField(verbose_name=_('enrollment start date'),
        db_index=True, null=True, blank=True)
    enrollment_end_date = models.DateTimeField(verbose_name=_('enrollment end date'),
        db_index=True, null=True, blank=True)
    thumbnails_info = JSONField(_('thumbnails info'), blank=True, null=True)

    objects = CourseManager()

    class Meta:
        ordering = ('-score',)
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def __unicode__(self):
        return _('Course {}').format(self.key)

    def get_absolute_url(self):
        return reverse('about_course', args=[self.key])

    def get_thumbnail_url(self, thumbnail_alias):
        url = ''
        try:
            url = self.thumbnails_info[thumbnail_alias]
        except (KeyError, TypeError):
            pass
        return url

    @property
    def first_university(self):
        try:
            first = self.related_universities.all()[0].university
        except IndexError:
            first = None
        return first

    @property
    def session_display(self):
        display_text = ''
        if self.session_number == 1:
            if self.enrollment_end_date and self.enrollment_end_date < now():
                display_text = ugettext('session 1')
            else:
                display_text = ugettext('new course')
        if self.session_number > 1:
            display_text = ugettext('session {}'.format(self.session_number))
        return display_text

    @property
    def university_name(self):
        if self.university_display_name:
            return self.university_display_name
        if self.first_university:
            return self.first_university.get_short_name()
        return ''

    @property
    def start_date_display(self):
        if not self.start_date:
            return ''
        return self.start_date.strftime(ugettext(u'%b %d %Y'))

    @property
    def enrollment_ended(self):
        return now() > self.enrollment_end_date if self.enrollment_end_date else False



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
        url = reverse('fun-courses-index')
        url = format('{}#filter/subject/{}/'.format(url, self.slug))
        return url

    def get_short_name(self):
        return self.short_name or self.name


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
        unique_together = ('university', 'course')

    def __unicode__(self):
        return u'{} - {}'.format(self.university, self.course)
