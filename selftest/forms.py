# -*- coding: utf-8 -*-

from django import forms


DEFAULT_EMAIL_RECIPIENT = 'richard@openfun.fr'

class EmailForm(forms.Form):
    to = forms.EmailField(max_length=100, initial=DEFAULT_EMAIL_RECIPIENT)
    text = forms.CharField(max_length=500, initial='manually sent self diagnostic email')
