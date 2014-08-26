# -*- coding: utf-8 -*-

from django.conf.urls import url, include, patterns


urlpatterns = patterns( '',

    (r'^selftest/', include('selftest.urls')),

    (r'^', include('cms.urls')),
)
