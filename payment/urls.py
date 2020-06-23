# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns
from django.conf import settings

# this url file is namespaced 'payment'

urlpatterns = patterns('payment.views',
    url(r'^success/$', 'paybox_success', name="success"),
    url(r'^cancel/$', 'paybox_cancel', name="cancel"),
    url(r'^error/$', 'paybox_error', name="error"),
    url(r'^receipt/$', 'list_receipts', name="list-receipts"),
    url(r'^receipt/(?P<order_id>\w*\-\d*)/$', 'detail_receipt', name="detail-receipt"),

    url(r'^terms(?:/(?P<force>(agreement)))?/$', 'payment_terms_page', name="terms-page"),
    url(r'^terms/get/$', 'get_payment_terms', name="get-terms"),
    url(r'^terms/accept/$', 'accept_payment_terms', name="accept-terms"),
)

if settings.FEATURES.get('ENABLE_PAYMENT_FAKE'):
    from tests.fun_fake_payment import PaymentFakeView
    urlpatterns += patterns(
        'payment.tests.fun_fake_payment',
        url(r'^fun_payment_fake', PaymentFakeView.as_view()),
    )
