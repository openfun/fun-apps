# -*- coding: utf-8 -*-

from django.conf.urls import include, url, patterns

urlpatterns = patterns('payment.views',
    url(r'^success/$', 'paybox_success', name="payment-success"),
    url(r'^notification/$', 'paybox_notification', name="payment-notification"),
    url(r'^cancel/$', 'paybox_cancel', name="payment-cancel"),
)


