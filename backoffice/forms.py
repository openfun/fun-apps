# -*- coding: utf-8 -*-
from django import forms
from django.forms.formsets import BaseFormSet

from django.utils.translation import ugettext_lazy as _

class RequiredFormSet(BaseFormSet):
    '''Make the first set Mandatory'''
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False

class StudentCertificateForm(forms.Form):
    full_name = forms.CharField(max_length=100, label=_(u"Full name"))

class TeachersCertificateForm(forms.Form):
    MAX_TEACHERS = 4
    full_name = forms.CharField(max_length=100, label=_(u"Full Name"))
    title = forms.CharField(max_length=100, label=_(u"Title"))
