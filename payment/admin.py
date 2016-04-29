# -*- coding: utf-8 -*-

from django.contrib import admin

from .models import TermsAndConditions, UserAcceptance

class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'version', 'datetime',)
    list_filter = ('name',)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:  # existing instances are not
            return self.fields or [f.name for f in self.model._meta.fields]
        else:
            return []

admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)

admin.site.register(UserAcceptance)


