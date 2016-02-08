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
from verify_student.models import SoftwareSecurePhotoVerification


from commerce import ecommerce_api_client


@csrf_exempt
def paybox_success(request):

    #http://localhost:8000/payment/success/?amount=10000&reference-fun=EDX-100056&autorisation=XXXXXX&erreur=00000&appel-paybox=16047443&transaction-paybox=7558206
    if getattr(settings, 'FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION', False):
        __ = requests.post(settings.ECOMMERCE_NOTIFICATION_URL, request.GET)

    if getattr(settings, 'FUN_ECOMMERCE_AUTOMATIC_VERIFICATION', False):
        verif, __ = SoftwareSecurePhotoVerification.objects.get_or_create(
                user=request.user,
                display=False,
                status='approved',
                reviewing_user=request.user,
                reviewing_service='automatic Paybox',
                )

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

    __ = requests.post(settings.ECOMMERCE_NOTIFICATION_URL, request.POST)

    return HttpResponse()  # Paybox do not expects any response
