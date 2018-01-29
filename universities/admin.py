from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

import fun.utils
from universities.models import University
import videoproviders.admin


class UniversityAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'short_name', 'preview', 'code', 'slug', 'detail_page_enabled',
        'is_obsolete', 'partnership_level', 'score')
    list_editable = ('score',)
    list_filter = ('detail_page_enabled', 'is_obsolete', 'partnership_level')
    search_fields = ('name', 'code', 'short_name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'short_name', 'code'),
                ('logo',),
                ('certificate_logo',),
                'partnership_level',
                'score',
            )
        }),
        (_('Advanced'), {
            'fields': (
                'prevent_auto_update',
            )
        }),
        (_('Displayed On Site | Banner | Description'), {
            'fields': (
                ('detail_page_enabled',),
                ('is_obsolete',),
                ('slug',),
                ('banner',),
                ('description',),
            )
        }),
    )
    inlines = [
        videoproviders.admin.YoutubeAuthAdminInline,
        videoproviders.admin.VideofrontAuthAdminInline,
    ]

    def preview(self, obj):
        template = u"""<img src="{url}" style="max-height: 48px;" />"""
        url = obj.logo.url if obj.logo else ''
        return template.format(url=url)
    preview.short_description = _('preview')
    preview.allow_tags = True


if fun.utils.is_lms_running():
    # Don't administer universities in cms. Logo file storage would not work.
    admin.site.register(University, UniversityAdmin)
