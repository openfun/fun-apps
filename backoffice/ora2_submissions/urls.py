# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

urlpatterns = patterns('backoffice.ora2_submissions.views',
    url(r'^/$', 'status', name='status'),
    url(r'^download/$', 'download', name='download'),
    url(r'^prepare/$', 'prepare', name='prepare'),
)
