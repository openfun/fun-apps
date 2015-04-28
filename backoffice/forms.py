# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.forms.formsets import BaseFormSet
from django.forms.models import BaseInlineFormSet
from django.utils.translation import ugettext_lazy as _

from student.models import UserProfile


class StudentCertificateForm(forms.Form):
    full_name = forms.CharField(max_length=100, label=_(u"Full name"))


class FirstRequiredFormSet(BaseInlineFormSet):
    """Teacher formset, at least one teacher is required."""
    def __init__(self, *args, **kwargs):
        super(FirstRequiredFormSet, self).__init__(*args, **kwargs)
        self.forms[0].empty_permitted = False
        for form in self.forms:
            form.fields['order'].widget = forms.HiddenInput()
            form.fields['title'].widget.attrs={'class': 'form-control'}
            form.fields['full_name'].widget.attrs={'class': 'form-control'}

    def clean(self):
        form = self.forms[0]
        if not form.is_valid():
            form._errors[forms.forms.NON_FIELD_ERRORS] = form.error_class([_(u"Please enter at least one teacher name")])


class SearchUserForm(forms.Form):
    search = forms.CharField(required=False)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)


class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            if 'rows' in field.widget.attrs:
                field.widget.attrs['rows'] = 3
    class Meta:
        model = UserProfile
        fields = ('name', 'gender', 'language', 'level_of_education', 'location',
            'year_of_birth', 'mailing_address', 'city', 'country', 'goals')
