# -*- coding: utf-8 -*-

import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, HttpResponseBadRequest, Http404
from django.views.decorators.csrf import csrf_exempt

import slumber.exceptions

from commerce import ecommerce_api_client
from edxmako.shortcuts import render_to_response
from verify_student.models import SoftwareSecurePhotoVerification

from courses.models import Course


def get_order_or_404(user, order_id):
    try:
        return ecommerce_api_client(user).orders(order_id).get()
    except (slumber.exceptions.HttpNotFoundError, slumber.exceptions.HttpClientError):
        raise Http404

def get_course(order):
    """Retrieve course corresponding to order.

    If the course does not exist, this will raise a 500 error.
    """
    try:
        attributes = order['lines'][0]['product']['attribute_values']
        course_key = [d['value'] for d in attributes if d['name'] == 'course_key'][0]
    except (KeyError, IndexError):
        raise Http404
    return Course.objects.get(key=course_key)


@csrf_exempt
@login_required
def paybox_success(request):
    """Called at the end of a successful payment.

    E.g arguments: amount=10000&reference-fun=EDX-100056&autorisation=XXXXXX&reponse-paybox=00000&appel-paybox=16047443&transaction-paybox=7558206
    """

    # TODO: find a smart way to factorize the control logic upon the 3 views
    if request.GET.get('reponse-paybox') != '00000' or not request.GET.get('reference-fun'):
        return HttpResponseBadRequest()

    if settings.FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION:
        # TODO what should we do with the response?
        _response = requests.post(settings.ECOMMERCE_NOTIFICATION_URL, request.GET)

    order = get_order_or_404(request.user, request.GET['reference-fun'])
    course = get_course(order)

    if settings.FUN_ECOMMERCE_AUTOMATIC_VERIFICATION:
        if not SoftwareSecurePhotoVerification.objects.filter(user=request.user).exists():
            _verif = SoftwareSecurePhotoVerification.objects.create(
                user=request.user,
                display=False,
                status='approved',
                reviewing_user=request.user,
                reviewing_service='automatic Paybox',
            )

    return render_to_response('payment/success.html', {
        'order': order,
        'order_course': course,
    })


@csrf_exempt
@login_required
def paybox_error(request):

    errorcode = request.GET.get('reponse-paybox')

    if errorcode is None or errorcode in ('0000', '00001') or not request.GET.get('reference-fun'):
        return HttpResponseBadRequest()

    order = get_order_or_404(request.user, request.GET['reference-fun'])
    course = get_course(order)

    return render_to_response('payment/error.html', {
        'errorcode': errorcode,
        'order': order,
        'order_course': course,
    })


@csrf_exempt
@login_required
def paybox_cancel(request):
    """User clicked on 'Cancel' before entering card information."""
    if request.GET.get('reponse-paybox') != '00001' or not request.GET.get('reference-fun'):
        return HttpResponseBadRequest()

    order = get_order_or_404(request.user, request.GET['reference-fun'])
    course = get_course(order)

    return render_to_response('payment/cancel.html', {
        'order': order,
        'order_course': course,
    })



@csrf_exempt
@login_required
def paybox_notification(request):
    """This view will proxy Paybox notifications to ecommerce service,
    to avoid internet exposition of bank VM.

    E.g: ?amount=10000&reference-fun=EDX-100072&autorisation=XXXXXX&reponse-paybox=00003&appel-paybox=16100769&transaction-paybox=7577769
    """

    __ = requests.post(settings.ECOMMERCE_NOTIFICATION_URL, request.POST)

    return HttpResponse()  # Paybox does not expect any response
