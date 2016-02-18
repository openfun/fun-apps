# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from edxmako.shortcuts import render_to_response

from commerce import ecommerce_api_client


@csrf_exempt
def fake_payment_page(request):
    
    return render_to_response('payment/fake.html', {
        'fields': request.POST,
        })


@csrf_exempt
def postpay_success(request):
    import ipdb; ipdb.set_trace()

    order = request.GET['order']

    order = ecommerce_api_client(request.user).baskets(order).order.get()



    return render_to_response('payment/return.html', {
        
        })

@csrf_exempt
def postpay_cancel(request):

    return render_to_response('payment/cancel.html', {
        })
