# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.utils import translation

from .views import index

static_pages = ("register_info",)
legal_pages = ("charte",)

richie_url = getattr(settings, "PLATFORM_RICHIE_URL", "")
current_language = translation.get_language()

cms_pages = {
    "about": "{base_url:s}/{lang:s}/a-propos".format(
        base_url=richie_url, lang=current_language
    ),
    "cours": "{base_url:s}/{lang:s}/cours".format(
        base_url=richie_url, lang=current_language
    ),
    "honor": "{base_url:s}/{lang:s}/charte-utilisateurs".format(
        base_url=richie_url, lang=current_language
    ),
    "legal": "{base_url:s}/{lang:s}/mentions-legales".format(
        base_url=richie_url, lang=current_language
    ),
    "privacy": "{base_url:s}/{lang:s}/politique-de-confidentialite".format(
        base_url=richie_url, lang=current_language
    ),
    "tos": "{base_url:s}/{lang:s}/cgu".format(
        base_url=richie_url, lang=current_language
    ),
    "news": "{base_url:s}/{lang:s}/actualites".format(
        base_url=richie_url, lang=current_language
    ),
    "universities": "{base_url:s}/{lang:s}/etablissements".format(
        base_url=richie_url, lang=current_language
    ),
}

urls = (url(r"^$", RedirectView.as_view(url=richie_url, permanent=True), name="root"),)

urls += tuple(
    url(
        r"^{}/?$".format(name),
        TemplateView.as_view(template_name="funsite/static_templates/%s.html" % name),
        name=name,
    )
    for name in static_pages
)

urls += tuple(
    [
        url(
            r"^{}/?$".format(name),
            RedirectView.as_view(url="/payment/terms/#%s" % name, permanent=True),
            name=name,
        )
        for name in legal_pages
    ]
)

urls += tuple(
    [
        url(
            r"^{}/?$".format(name),
            RedirectView.as_view(url=uri, permanent=True),
            name=name,
        )
        for name, uri in cms_pages.items()
    ]
)

urls += (
    url(
        r"^searchprovider.xml$",
        TemplateView.as_view(
            template_name="funsite/static_templates/searchprovider.xml",
            content_type="text/xml",
        ),
        name="searchprovider.xml",
    ),
)

urlpatterns = patterns("django.views.generic.simple", *urls)
