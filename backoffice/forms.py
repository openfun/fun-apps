# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from microsite_configuration import microsite

from newsfeed.models import Article
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


class ArticleForm(forms.ModelForm):
    # Make sure that the datetime formats used for form rendering and JS parsing are the same.
    DATETIME_INPUT_FORMAT = '%d/%m/%Y %H:%M'
    DATETIME_INPUT_FORMAT_JS = 'DD/MM/YYYY HH:mm'
    created_at = forms.DateTimeField(
        input_formats=(DATETIME_INPUT_FORMAT,),
        widget=forms.DateTimeInput(format=DATETIME_INPUT_FORMAT),
    )

    class Meta:
        model = Article
        fields = ['title', 'slug', 'created_at', 'thumbnail', 'language',
            'category', 'lead_paragraph', 'text', 'published',]

    def save(self, *args, **kwargs):
        if settings.FEATURES['USE_MICROSITES']:
            self.instance.microsite = microsite.get_value('SITE_NAME')
        instance = super(ArticleForm, self).save(*args, **kwargs)
        # For some reason, the 'thumbnail' field of the form remains an
        # InMemoryUploadedFile after the model has been modified and saved, and
        # it is not displayed in the frontend
        self.files['thumbnail'] = instance.thumbnail
        return instance
