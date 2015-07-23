# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

# namespace='faq'

urlpatterns = patterns('faq.views',
    url(r'^$', 'index', name='index'),
    url(r'^article/(?P<article_id>[\d]+)/$', 'article', name='article'),

)
