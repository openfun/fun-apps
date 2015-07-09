# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from student.models import UserProfile


class StudentCertificateForm(forms.Form):
    full_name = forms.CharField(max_length=100, label=_(u"Full name"))


class SearchUserForm(forms.Form):
    search = forms.CharField(required=False)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # i18n fields labels and choices
        for field in self.fields.values():
            if 'rows' in field.widget.attrs:
                field.widget.attrs['rows'] = 3
            field.label = _(field.label)
            if isinstance(field, forms.fields.TypedChoiceField):
                field.choices = [(key, _(value)) for key, value in field.choices]

    class Meta:
        model = UserProfile
        fields = ('name', 'gender', 'language', 'level_of_education', 'location',
            'year_of_birth', 'mailing_address', 'city', 'country', 'goals')
