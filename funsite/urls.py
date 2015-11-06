# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


static_pages = ['about', 'honor', 'legal', 'privacy', 'tos', 'register_info']

urls = [url(r'^(?P<page>({}))/?$'.format(name),
             'render_static_template',
             name=name)
        for name in static_pages]

urlpatterns = patterns('funsite.views', *urls)
