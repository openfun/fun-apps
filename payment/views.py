# -*- coding: utf-8 -*-

import logging

import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from edxmako.shortcuts import render_to_response

from commerce import ecommerce_api_client

ECOMMERCE_NOTIFICATION_URL = 'http://localhost:8002/payment/paybox/notify/'

@csrf_exempt
def paybox_success(request):


    return render_to_response('payment/return.html', {
        
        })

@csrf_exempt
def paybox_cancel(request):

    return render_to_response('payment/cancel.html', {
        })


@csrf_exempt
def paybox_notification(request):
    """This view will proxy Paybox notifications to ecommerce service,
    to avoid internet exposition of bank VM."""

    

    __ = requests.post(ECOMMERCE_NOTIFICATION_URL, request.POST)

    return HttpResponse()  # Paybox do not expects any response
