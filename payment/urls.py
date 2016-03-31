# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

urlpatterns = patterns('payment.views',
    url(r'^success/$', 'paybox_success', name="success"),
    url(r'^cancel/$', 'paybox_cancel', name="cancel"),
    url(r'^error/$', 'paybox_error', name="error"),
    url(r'^receipt/$', 'list_receipts', name="list-receipts"),
    url(r'^receipt/(?P<order_id>\w*\-\d*)/$', 'detail_receipt', name="detail-receipt"),
)
