# -*- coding: utf-8 -*-

from django.conf.urls import include, url, patterns

urlpatterns = patterns('payment.views',
    url(r'^fake-payment-page/$', 'fake_payment_page', name="payment-fake"),

    url(r'^postpay-success/$', 'postpay_success', name="payment-success"),
    url(r'^postpay-cancel/$', 'postpay_cancel', name="payment-cancel"),
)


