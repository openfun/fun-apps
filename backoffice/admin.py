# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from student.models import LoginFailures

from .models import Course, Teacher


admin.site.register(Course)
admin.site.register(Teacher)


class LoginFailuresProxy(LoginFailures):
    class Meta:
        proxy = True
        verbose_name = _(u"Temporary account suspension")
        verbose_name_plural = _(u"Temporary account suspensions")


class LoginFailuresAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    search_fields = ('user__last_name', 'user__username', 'user__email')
    list_display = ('user', 'lockout_until', 'failure_count')
admin.site.register(LoginFailuresProxy, LoginFailuresAdmin)