# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView


static_pages = ['about', 'honor', 'legal', 'privacy', 'tos', 'register_info',
        'proctoru', 'contact']

urls = [
    url(r'^{}/?$'.format(name), TemplateView.as_view(template_name='funsite/static_templates/%s.html' % name), name=name)
    for name in static_pages
]

urls.append(
    url(r'^searchprovider.xml$', TemplateView.as_view(template_name='funsite/static_templates/searchprovider.xml', content_type='text/xml'),
        name='searchprovider.xml')
)

urlpatterns = patterns('django.views.generic.simple', *urls)
