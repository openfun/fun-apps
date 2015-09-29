# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from teachers.admin import CourseTeacherInline, CertificateTeacherInline

from .models import Course, CourseSubject, CourseUniversityRelation


class CourseUniversityRelationInline(admin.TabularInline):
    model = CourseUniversityRelation
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    list_display = ('key', 'title', 'level', 'score', 'session_number',
        'is_active', 'prevent_auto_update',
        'modification_date')
    list_filter = ('is_active', 'prevent_auto_update',
        'level', 'subjects', 'universities')
    search_fields = ('key', 'title', 'short_description',
        'certificateteacher_related__teacher__full_name',
        'courseteacher_related__teacher__full_name', )
    filter_horizontal = ('subjects',)
    inlines = (
        CourseUniversityRelationInline,
        CourseTeacherInline,
        CertificateTeacherInline,
    )
    list_editable = ('score',)
    fieldsets = (
        (None, {
            'fields': (
                'key',
                'title',
                'image_url',
                'short_description',
                'level',
                'subjects',
                'session_number',
                'score',
            )
        }),
        (None, {
            'fields': (
                'is_active',
                'prevent_auto_update',
            )
        }),
        (_('Availability'), {
            'fields': (
                ('start_date', 'end_date'),
            )
        }),
        (_('Advanced'), {
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
    preview.short_description=_('preview')
    preview.allow_tags = True

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseSubject, CourseSubjectAdmin)
