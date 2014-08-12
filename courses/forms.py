# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext as _


class CourseFileteringForm(forms.Form):
    STATE_CHOICES = (
        ('ALL', _(u"All")),
        ('FUTURE', _(u"Incoming")),
        ('CURRENT', _(u"Current")),
        ('PAST', _(u"Past")),
        )

    state = forms.ChoiceField(choices=STATE_CHOICES, label=_(u"State"))
    theme = forms.ChoiceField(choices=[], required=False, label=_(u"Theme"))
    university = forms.ChoiceField(choices=[], required=False, label=_(u"University"))

    def __init__(self, *args, **kwargs):
        super(CourseFileteringForm, self).__init__(*args, **kwargs)