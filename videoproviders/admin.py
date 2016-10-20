from django.contrib import admin

from . import models


class VideoUploaderDeactivationPeriodAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time')


class YoutubeAuthAdminInline(admin.StackedInline):
    model = models.YoutubeAuth
    fields = ("client_id", "client_secret", "access_token", "refresh_token", "token_expiry",)


class YoutubeCourseSettingsAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'playlist_id')


class VideofrontCourseSettingsAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'playlist_id')
    search_fields = ('course_id', 'playlist_id')


class VideofrontAuthAdminInline(admin.StackedInline):
    model = models.VideofrontAuth
    fields = ("token",)


admin.site.register(models.VideoUploaderDeactivationPeriod, VideoUploaderDeactivationPeriodAdmin)
admin.site.register(models.YoutubeCourseSettings, YoutubeCourseSettingsAdmin)
admin.site.register(models.VideofrontCourseSettings, VideofrontCourseSettingsAdmin)
