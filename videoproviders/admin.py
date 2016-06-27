from django.contrib import admin

from . import models


class LibcastAuthAdminInline(admin.StackedInline):
    model = models.LibcastAuth
    fields = ("username", "api_key",)


class LibcastCourseSettingsAdmin(admin.ModelAdmin):
    list_display = ('course',)


class VideoUploaderDeactivationPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time')


class YoutubeAuthAdminInline(admin.StackedInline):
    model = models.YoutubeAuth
    fields = ("client_id", "client_secret", "access_token", "refresh_token", "token_expiry",)


class YoutubeCourseSettingsAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'playlist_id')


admin.site.register(models.LibcastCourseSettings, LibcastCourseSettingsAdmin)
admin.site.register(models.VideoUploaderDeactivationPeriod, VideoUploaderDeactivationPeriodAdmin)
admin.site.register(models.YoutubeCourseSettings, YoutubeCourseSettingsAdmin)
