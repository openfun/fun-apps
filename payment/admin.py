# -*- coding: utf-8 -*-

from django.contrib import admin
from datetime import datetime as dt
from django.db import models
from django.forms import forms
from django.db import models
from django.forms import Textarea
from .models import TermsAndConditions, UserAcceptance, TranslatedTerms
from django.forms import ModelChoiceField,BaseInlineFormSet
from django.conf import settings

SUPPORTED_LANGUAGES = tuple(l[0] for l in settings.LANGUAGES)
PREF_MARKDOWN = dict(
    rows = 40,
    cols = 100,
    style = 'font-family:monospace'
)

now =  dt.now()
now = now.replace(tzinfo=None)

class TranslatedInlineFormset(BaseInlineFormSet):
    def __init__(self, *a, **kw):
        kw['initial'] = [dict(language=lang) for lang in SUPPORTED_LANGUAGES]
        parent_id=kw.get("parent_id", None)
        self.parent=None
        obj= kw.get("instance")
        super(TranslatedInlineFormset, self).__init__(*a, **kw)
        self._readonly_fields = []


class TranslatedTermsInline(admin.StackedInline):
    model = TranslatedTerms
    class Meta:
        model = TranslatedTerms
    formfield_overrides = {
        models.TextField: dict(widget=Textarea(attrs=PREF_MARKDOWN))
    }

    fk_name = "term"
    extra = max_num = len(SUPPORTED_LANGUAGES)
    formset = TranslatedInlineFormset



class TermsAndConditionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'version', 'datetime',)
    exclude = ('text',)
    list_filter = ('name',)
    class Meta:
        model = TermsAndConditions

    inlines = (TranslatedTermsInline,)
    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        RO_FIELD = tuple()
        if not obj or not obj.datetime:
            return RO_FIELD
        term_dt = obj.datetime
        term_dt = term_dt.replace(tzinfo=None)
        return (term_dt < now) \
            and TermsAndConditionsAdmin.list_display \
            or RO_FIELD

admin.site.register(
    TermsAndConditions,
    TermsAndConditionsAdmin,
)

class UserAcceptanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'terms', 'datetime',)
    search_fields = ('user__username',)
    raw_id_fields = ('user',)

admin.site.register(UserAcceptance, UserAcceptanceAdmin)

class TranslatedTermsAdmin(admin.ModelAdmin):
    list_display = ('id', 'term', 'tr_text', 'language',)
    raw_id_fields = ['term']
    formfield_overrides = {
        models.TextField: dict(widget=Textarea(attrs=PREF_MARKDOWN))
    }


admin.site.register(
    TranslatedTerms,
    TranslatedTermsAdmin
)



