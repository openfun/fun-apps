from django.contrib import admin

from . import models


class LibcastAuthAdminInline(admin.StackedInline):
    model = models.LibcastAuth
    fields = ("username", "api_key",)


class LibcastCourseSettingsAdmin(admin.ModelAdmin):
    list_display = ('course',)


class VideoUploaderDeactivationPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time')


admin.site.register(models.LibcastCourseSettings, LibcastCourseSettingsAdmin)
admin.site.register(models.VideoUploaderDeactivationPeriod, VideoUploaderDeactivationPeriodAdmin)
