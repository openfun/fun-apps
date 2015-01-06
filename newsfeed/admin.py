import datetime

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from adminsortable.admin import SortableAdminMixin
from solo.admin import SingletonModelAdmin

from . import models

class ArticleAdminForm(forms.ModelForm):

    class Meta:
        model = models.Article
        widgets = {
            "title": forms.TextInput(attrs={"size": 100})
        }

    def __init__(self, *args, **kwargs):
        super(ArticleAdminForm, self).__init__(*args, **kwargs)
        if "instance" not in kwargs:
            # Instance is being created
            self.fields['created_at'].initial = datetime.datetime.now()


class FeaturedSectionAdmin(SingletonModelAdmin):
    raw_id_fields = ('article',)


class ArticleAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = ArticleAdminForm
    change_form_template = "newsfeed/change_form.html"

    list_display = ("title", "preview", "published", "created_at",)
    readonly_fields = ("edited_at",)# TODO display that
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ("title", "text", "slug",)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "language", "thumbnail",
                ("published", "created_at"), "text",
            )
        }),
    )

    def preview(self, obj):
        template = u"""<img src="{url}" style="max-height: 48px;" />"""
        url = obj.thumbnail.url if obj.thumbnail else ''
        return template.format(url=url)
    preview.short_description=_('preview')
    preview.allow_tags = True

admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.FeaturedSection, FeaturedSectionAdmin)
