# -*- coding: utf-8 -*-

from django.contrib import admin

from adminsortable.admin import SortableAdminMixin

from teachers.admin import CourseTeacherInline, CertificateTeacherInline

from .models import Course, CourseSubject


class CourseAdmin(admin.ModelAdmin):
    list_display = ('key', 'university', 'level')
    list_filter = ('level', 'subjects', 'university')
    search_fields = ('key',)
    filter_horizontal = ('subjects',)
    inlines = (CourseTeacherInline, CertificateTeacherInline)
    fieldsets = (
        (None, {
            'fields': (
                'key',
                'university',
                'level',
                'subjects',
            )
        }),
    )


class CourseSubjectAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug',)
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Course, CourseAdmin)
admin.site.register(CourseSubject, CourseSubjectAdmin)
