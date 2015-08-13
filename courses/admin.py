# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from adminsortable.admin import SortableAdminMixin

from teachers.admin import CourseTeacherInline, CertificateTeacherInline

from .models import Course, CourseSubject, CourseUniversityRelation


class CourseUniversityRelationInline(admin.TabularInline):
    model = CourseUniversityRelation
    extra = 1


class CourseAdmin(admin.ModelAdmin):
    list_display = ('key', 'level', 'score')
    list_filter = ('level', 'subjects', 'universities')
    search_fields = ('key', 'certificateteacher_related__teacher__full_name',
        'courseteacher_related__teacher__full_name')
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
                'level',
                'subjects',
                'score',
            )
        }),
    )


class CourseSubjectAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'preview', 'featured')
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
