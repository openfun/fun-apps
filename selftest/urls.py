# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('selftest.views',
    url(r'^$', 'selftest_index', name='self-test-index'),
    url(r'^page_not_found/$', 'page_not_found', name='self-test-404'),
    url(r'^server_error/$', 'server_error', name='self-test-500'),
    url(r'^worker_error/$', 'worker_error', name='worker-error')
)
