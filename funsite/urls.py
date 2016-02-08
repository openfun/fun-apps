# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


static_pages = ['about', 'honor', 'legal', 'privacy', 'tos', 'register_info']

urls = [
    url(r'^{}/?$'.format(name), 'direct_to_template', kwargs={'template': 'funsite/static_templates/%s.html' % name}, name=name)
    for name in static_pages
]

urlpatterns = patterns('django.views.generic.simple', *urls)
