# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.forms import ModelForm, ModelChoiceField
from chosen import forms as chosenforms

from .models import CourseTeacher, CertificateTeacher, Teacher


class CertificateTeacherRelationInlineForm(ModelForm):
    teacher = chosenforms.ChosenModelChoiceField(queryset=Teacher.objects.all().order_by("slug"))


class CourseTeacherRelationInlineForm(ModelForm):
    teacher = chosenforms.ChosenModelChoiceField(queryset=Teacher.objects.all().order_by("slug"))


class CourseTeacherInline(admin.TabularInline):
    '''
    Can be used where editing teachers inline is needed,
    for instance on course admin page.
    '''
    model = CourseTeacher
    form = CourseTeacherRelationInlineForm
    extra = 1


class CertificateTeacherInline(admin.TabularInline):
    '''
    Can be used where editing teachers inline is needed,
    for instance on course admin page.
    '''
    model = CertificateTeacher
    extra = 1
    form = CertificateTeacherRelationInlineForm


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'preview', 'slug')
    search_fields = ('full_name', 'bio', 'slug')
    prepopulated_fields = {'slug': ('full_name',)}

    def preview(self, obj):
        template = u"""<img src="{url}" style="max-height: 48px;" />"""
        url = obj.profile_image.url if obj.profile_image else ''
        return template.format(url=url)
    preview.short_description=_('preview')
    preview.allow_tags = True


admin.site.register(Teacher, TeacherAdmin)
