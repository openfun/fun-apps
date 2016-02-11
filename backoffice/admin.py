# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from djcelery.models import TaskMeta, TaskSetMeta

from student.models import LoginFailures


# proxy models allow us to override django_celery admin settings.
class TaskMetaProxy(TaskMeta):
    class Meta:
        proxy = True
        verbose_name = _(u"Celery task result")
        verbose_name_plural = _(u"Celery task results")


class TaskSetMetaProxy(TaskSetMeta):
    class Meta:
        proxy = True
        verbose_name = _(u"Celery taskset result")
        verbose_name_plural = _(u"Celery taskset results")


class TaskMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('task_id', 'status', 'date_done', 'hidden', 'meta', 'result', 'traceback')
    search_fields = ('id', 'task_id',)
    list_display = ('id', 'task_id', 'status', 'date_done')
    list_filter = ('status', 'hidden')

    def has_delete_permission(self, request, obj=None):
        return False  # results are read only and can not be deleted


class TaskSetMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('taskset_id', 'date_done', 'hidden', 'result',)
    search_fields = ('id', 'taskset_id',)
    list_display = ('id', 'taskset_id', 'date_done', 'hidden', )
    list_filter = ('hidden',)

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(TaskMetaProxy, TaskMetaAdmin)
admin.site.register(TaskSetMetaProxy, TaskSetMetaAdmin)


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
