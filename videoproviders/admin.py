from django.contrib import admin

from . import models


class LibcastAuthAdminInline(admin.StackedInline):
    model = models.LibcastAuth
    fields = ("username", "api_key",)


class LibcastCourseSettingsAdmin(admin.ModelAdmin):
    list_display = ('course',)

admin.site.register(models.LibcastCourseSettings, LibcastCourseSettingsAdmin)
