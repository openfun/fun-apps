# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

urlpatterns = patterns('backoffice.certificate_manager.views',
    url(r'^dashboard$', 'certificate_dashboard', name='certificate-dashboard'),
    url(r'^generate_test$', 'generate_test_certificate', name='generate-test-certificate'),
    url(r'^generate$', 'generate_certificate', name='generate-certificates'),
    url(r'^generate_verified$', 'generate_certificate', {'verified': True}, name='generate-verified-certificates'),
)

