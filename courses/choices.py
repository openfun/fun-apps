# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _


COURSE_LEVEL_INTRODUCTORY = 'introductory'
COURSE_LEVEL_INTERMEDIATE = 'intermediate'
COURSE_LEVEL_ADVANCED = 'advanced'

COURSE_LEVEL_CHOICES = (
    (COURSE_LEVEL_INTRODUCTORY, _('Introductory')),
    (COURSE_LEVEL_INTERMEDIATE, _('Intermediate')),
    (COURSE_LEVEL_ADVANCED, _('Advanced')),
)

# Please maintain alphabetical order for test consistancy
COURSE_LANGUAGES = (('de', _('German')), ('en', _('English')), ('fr', _('French')))

