from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from adminsortable.admin import SortableAdminMixin

from universities.models import University


class UniversityAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'preview', 'code', 'slug', 'featured')
    list_filter = ('featured',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'code'),
                ('logo',),
                ('certificate_logo',),
                ('parent',),
            )
        }),
        (_('Daily Motion'), {
            'fields': (
                ('dm_user_id',),
                ('dm_api_key',),
            )
        }),
        (_('Displayed On Site | Banner | Description'), {
            'fields': (
                ('featured',),
                ('slug',),
                ('banner',),
                ('description',),
            )
        }),
    )

    def preview(self, obj):
        template = u"""<img src="{url}" style="max-height: 48px;" />"""
        url = obj.logo.url if obj.logo else ''
        return template.format(url=url)
    preview.short_description=_('preview')
    preview.allow_tags = True


admin.site.register(University, UniversityAdmin)
