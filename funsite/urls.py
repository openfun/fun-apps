# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView, RedirectView


static_pages = ('about', 'register_info', 'proctoru', )
legal_pages =('honor','legal','privacy','tos', 'charte', )

urls = tuple(
    url(r'^{}/?$'.format(name), TemplateView.as_view(template_name='funsite/static_templates/%s.html' % name), name=name)
    for name in static_pages
)

urls += tuple([
    url(
        r'^{}/?$'.format(name),
        RedirectView.as_view(
            url='/payment/terms/#%s' % name, permanent=True), name=name
    ) for name in legal_pages
])

urls += (
    url(r'^searchprovider.xml$',
        TemplateView.as_view(
            template_name='funsite/static_templates/searchprovider.xml',
            content_type='text/xml'
        ),
        name='searchprovider.xml'
    ),
)

urlpatterns = patterns('django.views.generic.simple', *urls)
