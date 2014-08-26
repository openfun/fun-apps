# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings

class EmailForm(forms.Form):
    to = forms.EmailField(max_length=100, initial=settings.SERVER_EMAIL)
    text = forms.CharField(max_length=500, initial='manually sent self diagnostic email')
