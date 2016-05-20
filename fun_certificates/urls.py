# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns('fun_certificates.views',
    url(r'^cert/(?P<encoded_cert_id>[\w\d]+)/$', 'short_cert_url', name='short-cert-url'),
)
