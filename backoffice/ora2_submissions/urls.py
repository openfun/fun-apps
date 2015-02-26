# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

urlpatterns = patterns('backoffice.ora2_submissions.views',
    url(r'^prepare/$', 'prepare', name='prepare'),
    url(r'^download/$', 'download', name='download'),
    url(r'^$', 'status', name='status'),
)
