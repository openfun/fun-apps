# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


static_pages = ['about', 'honor', 'legal', 'privacy', 'tos', 'register_info',
        'proctoru']

urls = [
    url(r'^{}/?$'.format(name), 'direct_to_template',
        kwargs={'template': 'funsite/static_templates/%s.html' % name},
        name=name)
    for name in static_pages
]

urls.append(
    url(r'^searchprovider.xml$', 'direct_to_template',
        kwargs={
            'template': 'funsite/static_templates/searchprovider.xml',
            'mimetype': 'text/xml',
        },
        name='searchprovider.xml')
)

urlpatterns = patterns('django.views.generic.simple', *urls)
