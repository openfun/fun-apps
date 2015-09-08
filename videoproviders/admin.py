from django.contrib import admin

from . import models


class DailymotionAuthAdminInline(admin.StackedInline):
    model = models.DailymotionAuth
    fields = ("username", "password", "api_key", "api_secret", "access_token", "refresh_token", "expires_at_time",)
    readonly_fields = ("access_token", "refresh_token", "expires_at_time",)


class LibcastAuthAdminInline(admin.StackedInline):
    model = models.LibcastAuth
    fields = ("username", "api_key",)


class LibcastCourseSettingsAdmin(admin.ModelAdmin):
    list_display = ('course',)

admin.site.register(models.LibcastCourseSettings, LibcastCourseSettingsAdmin)
