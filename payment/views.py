# -*- coding: utf-8 -*-

import logging

import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from edxmako.shortcuts import render_to_response
from verify_student.models import SoftwareSecurePhotoVerification


from commerce import ecommerce_api_client




@csrf_exempt
@login_required
def paybox_success(request):
    # http://localhost:8000/payment/success/?amount=10000&reference-fun=EDX-100056&autorisation=XXXXXX&reponse-paybox=00000&appel-paybox=16047443&transaction-paybox=7558206

    if request.GET['reponse-paybox'] != '00000':
        raise Exception

    if settings.FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION:
        response = requests.post(settings.ECOMMERCE_NOTIFICATION_URL, request.GET)


    if settings.FUN_ECOMMERCE_AUTOMATIC_VERIFICATION:
        if not SoftwareSecurePhotoVerification.objects.filter(user=request.user).exists():
            verif = SoftwareSecurePhotoVerification.objects.create(
                user=request.user,
                display=False,
                status='approved',
                reviewing_user=request.user,
                reviewing_service='automatic Paybox',
            )

    return render_to_response('payment/success.html', {

    })


@csrf_exempt
@login_required
def paybox_error(request):

    errorcode = request.GET['reponse-paybox']

    if errorcode in ('0000', '00001'):
        raise Exception



    return render_to_response('payment/error.html', {
        'errorcode': errorcode,
    })


@csrf_exempt
@login_required
def paybox_cancel(request):
    """User clicked on 'Cancel' before entering card information."""
    if request.GET['reponse-paybox'] != '00001':
        raise Exception

    return render_to_response('payment/cancel.html', {
    })


#?amount=10000&reference-fun=EDX-100072&autorisation=XXXXXX&reponse-paybox=00003&appel-paybox=16100769&transaction-paybox=7577769

@csrf_exempt
@login_required
def paybox_notification(request):
    """This view will proxy Paybox notifications to ecommerce service,
    to avoid internet exposition of bank VM."""

    __ = requests.post(settings.ECOMMERCE_NOTIFICATION_URL, request.POST)

    return HttpResponse()  # Paybox do not expects any response
