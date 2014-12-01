import datetime

from django import forms
from django.contrib import admin

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


class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    change_form_template = "newsfeed/change_form.html"

    list_display = ("title", "created_at",)
    readonly_fields = ("edited_at",)# TODO display that
    search_fields = ("title", "text", "slug",)
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "language", ("published", "created_at"), "text",)
        }),
    )
    ordering = ("-created_at",)

admin.site.register(models.Article, ArticleAdmin)
