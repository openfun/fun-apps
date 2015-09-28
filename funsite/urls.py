# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

static_pages = r'(?P<page>(about|honor|legal|privacy|tos))'

urlpatterns = patterns('funsite.views',
    url(r'^{}/$'.format(static_pages), 'render_static_template',
            name='render_static_template'),
    )
