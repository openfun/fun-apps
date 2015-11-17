import datetime

from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

#from adminsortable.admin import SortableAdminMixin

from . import models


class ArticleLinkInline(admin.TabularInline):
    model = models.ArticleLink
    extra = 2


class ArticleAdminForm(forms.ModelForm):

    class Meta:
        model = models.Article
        widgets = {
            "title": forms.TextInput(attrs={"size": 100})
        }


class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    change_form_template = "newsfeed/change_form.html"

    list_display = ("title", "preview", "category", "language",
        "published", "created_at", "microsite",)
    list_filter = ("published", "category")
    filter_horizontal = ('courses',)
    readonly_fields = ("edited_at",)  # TODO display that
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ("title", "text", "slug",)
    inlines = (ArticleLinkInline,)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "language", "thumbnail",
                "category", "courses", "lead_paragraph",
                "event_date", ("published", "order", "created_at"),
                "microsite", "text",
            )
        }),
    )

    def preview(self, obj):
        template = u"""<img src="{url}" style="max-height: 48px;" />"""
        url = obj.thumbnail.url if obj.thumbnail else ''
        return template.format(url=url)
    preview.short_description = _('preview')
    preview.allow_tags = True

admin.site.register(models.Article, ArticleAdmin)
admin.site.register(models.ArticleCategory, ArticleCategoryAdmin)
