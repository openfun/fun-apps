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

    def make_teachers_list(self):
        '''Return a list of teacher/title, format required by the module generator.py'''
        teachers = []

        for key in range(1, 4):
            if "teacher{}".format(key) in self.cleaned_data and "title{}".format(key) in self.cleaned_data:
                teachers.append("{}/{}".format(self.cleaned_data['teacher{}'.format(key)],
                                               self.cleaned_data['title{}'.format(key)]))
        return teachers

