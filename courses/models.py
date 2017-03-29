# -*- coding: utf-8 -*-

from time import time

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import date as django_localize_date
from django.utils.timezone import now
from django.utils.translation import ugettext, ugettext_lazy as _

from ckeditor.fields import RichTextField
from course_modes.models import CourseMode
from jsonfield.fields import JSONField

from . import choices as courses_choices
from .managers import CourseSubjectManager, CourseQuerySet


def localize_date(date_time):
    """Use Django template filter `date` to localize datetime and display month
    in full text in user's language."""
    if not date_time:
        return ''
    return django_localize_date(date_time, ugettext(u'b d Y'))


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
    subjects = models.ManyToManyField('CourseSubject', related_name='courses', blank=True)
    level = models.CharField(_('level'), max_length=255,
        choices=courses_choices.COURSE_LEVEL_CHOICES, blank=True, db_index=True)
    language = models.CharField(_('language'), max_length=255,
        choices=courses_choices.COURSE_LANGUAGES, default='fr', db_index=True)
    show_in_catalog = models.BooleanField(verbose_name=_('show in catalog'),
        default=False, db_index=True, help_text=_('Controls whether a course is '
        'listed in the courses catalog page'))
    show_about_page = models.BooleanField(verbose_name=_('show course about page'),
        default=True, db_index=True, help_text=_('Controls whether the course '
        'about page is visible'))
    is_active = models.BooleanField(verbose_name=_('is active'), default=False)
    prevent_auto_update = models.BooleanField(verbose_name=_('No auto update'),
        help_text=_('prevent score automatic update'), default=False)
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
    certificate_passing_grade = models.FloatField(_('verified certificate passing grade'),
        null=True, blank=True, help_text=(_('Percentage, between 0 and 1')))

    objects = CourseQuerySet.as_manager()

    # Cache the courses that have a verified mode. This allows us to write
    # course.has_verified_mode by running just one additional sql query for all
    # courses. This cache is local to the runtime and should expire frequently.
    _verified_course_key_strings_cache = [
        set(), # set of all course_key_string for courses that have a verified mode
        0      # timestamp at which this cache was last updated
    ]


    @property
    def has_verified_course_mode(self):
        """Return True if the course has at least one verified course mode.

        This information is collected from a cache that has an expire period of 10s.
        """
        if time() - self._verified_course_key_strings_cache[1] > 10:
            verified_course_modes = CourseMode.objects.filter(mode_slug__in=CourseMode.VERIFIED_MODES)
            Course._verified_course_key_strings_cache = (
                set([unicode(course_mode.course_id) for course_mode in verified_course_modes]),
                time()
            )
        return self.key in Course._verified_course_key_strings_cache[0]

    class Meta:
        ordering = ('-score',)
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def __unicode__(self):
        return _('Course {}').format(self.key)

    def get_absolute_url(self):
        return reverse('about_course', args=[self.key])

    def get_thumbnail_url(self, thumbnail_alias):
        # see settings.FUN_THUMBNAIL_OPTIONS for preprocessed thumbnails
        url = ''
        try:
            url = self.thumbnails_info[thumbnail_alias]
        except (KeyError, TypeError):
            pass
        return url

    @staticmethod
    def get_course_language(course_id):
        try:
            return Course.objects.get(key=course_id).language
        except Course.DoesNotExist:
            return None

    def get_first_university(self):
        '''
        First university in regard to the order field - that's how allow
        an admin person to decide who's the first / main university.
        '''
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
        first_university = self.get_first_university()
        if first_university:
            return first_university.get_short_name()
        return ''

    @property
    def start_date_display(self):
        return localize_date(self.start_date)

    @property
    def end_date_display(self):
        return localize_date(self.end_date)

    @property
    def enrollment_start_date_display(self):
        return localize_date(self.enrollment_start_date)

    @property
    def enrollment_end_date_display(self):
        return localize_date(self.enrollment_end_date)

    @property
    def enrollment_ended(self):
        return now() > self.enrollment_end_date if self.enrollment_end_date else False

    @property
    def course_started(self):
        return now() > self.start_date if self.start_date else False

    @property
    def course_ended(self):
        return now() > self.end_date if self.end_date else False


class CourseSubject(models.Model):
    name = models.CharField(_('name'), max_length=255, db_index=True)
    short_name = models.CharField(_('short name'), max_length=255, blank=True,
        help_text=_('Displayed where space is rare - on side panel for instance.'))
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    description = RichTextField(_('description'), blank=True)
    featured = models.BooleanField(verbose_name=_('featured'), db_index=True, default=False)
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
