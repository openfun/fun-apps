# -*- coding: utf-8 -*-

from django.contrib import admin
from django.forms import ModelForm, ModelChoiceField
from django.utils.translation import ugettext_lazy as _

from teachers.admin import CourseTeacherInline, CertificateTeacherInline
from universities.models import University

from . import settings as courses_settings
from .models import Course, CourseSubject, CourseUniversityRelation


class CourseUniversityRelationInlineForm(ModelForm):
    university = ModelChoiceField(queryset=University.objects.all().order_by("name"))


class CourseUniversityRelationInline(admin.TabularInline):
    model = CourseUniversityRelation
    extra = 1
    form = CourseUniversityRelationInlineForm


class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'certificate_passing_grade', 'key', 'is_active', 'level', 'modification_date', 'title',
        'score', 'session_number', 'show_about_page', 'show_in_catalog', 'prevent_auto_update')
    list_filter = (
        'is_active', 'level', 'show_in_catalog', 'show_about_page', 'prevent_auto_update',
        'subjects', 'universities')
    search_fields = (
        'certificateteacher_related__teacher__full_name',
        'courseteacher_related__teacher__full_name', 'key', 'title', 'short_description',
        'university_display_name')
    readonly_fields = courses_settings.COURSE_ADMIN_READ_ONLY_FIELDS
    filter_horizontal = ('subjects',)
    inlines = (
        CourseUniversityRelationInline,
        CourseTeacherInline,
        CertificateTeacherInline,
    )
    list_editable = ('score', 'session_number')
    fieldsets = (
        (_('Course Info'), {
            'fields': (
                'subjects',
                'session_number',
                'score',
                'certificate_passing_grade',
                'language'
            )
        }),
        (_('Course Info - Automatically Updated'), {
            'fields': (
                'key',
                'title',
                'university_display_name',
                'image_url',
                ('start_date', 'end_date'),
                ('enrollment_start_date', 'enrollment_end_date'),
            )
        }),
        (_('Visibility'), {
            'fields': (
                'show_in_catalog',
                'show_about_page',
            )
        }),
        (_('Advanced'), {
            'fields': (
                'prevent_auto_update',
                'is_active',
            )
        }),
        (_('Developer'), {
            'classes': ('collapse',),
            'fields': (
                'thumbnails_info',
            )
        }),
    )


class CourseSubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'slug', 'preview', 'featured', 'score')
    list_filter = ('featured',)
    prepopulated_fields = {'slug': ('name',)}

    def preview(self, obj):
        template = u"""<img src="{url}" style="max-height: 48px;" />"""
        url = obj.image.url if obj.image else ''
        return template.format(url=url)
    preview.short_description = _('preview')
    preview.allow_tags = True


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseSubject, CourseSubjectAdmin)
