# -*- coding: utf-8 -*-

from django import forms

class TestCertificateForm(forms.Form):
    full_name = forms.CharField(max_length=100)

    teacher1 = forms.CharField(max_length=100)
    title1 = forms.CharField(max_length=100)

    teacher2 = forms.CharField(max_length=100,required=False)
    title2 = forms.CharField(max_length=100, required=False)

    teacher3 = forms.CharField(max_length=100, required=False)
    title3 = forms.CharField(max_length=100, required=False)



