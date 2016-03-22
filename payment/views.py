# -*- coding: utf-8 -*-

import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponseBadRequest, Http404
from django.views.decorators.csrf import csrf_exempt

import slumber.exceptions

from edxmako.shortcuts import render_to_response

from .utils import get_order, get_course


def get_order_or_404(user, order_id):
    try:
        return get_order(user, order_id)
    except (slumber.exceptions.HttpNotFoundError, slumber.exceptions.HttpClientError):
        raise Http404()


def get_course_or_404(order):
    """Retrieve course corresponding to order.

    If the course does not exist, this will raise a 404 error.
    """
    try:
        course = get_course(order)
    except (KeyError, IndexError, ObjectDoesNotExist):
        raise Http404
    return course


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
    course = get_course_or_404(order)

    return render_to_response('payment/success.html', {
        'order': order,
        'order_course': course,
    })


@csrf_exempt
@login_required
def paybox_error(request):
    """Called on transaction error."""
    errorcode = request.GET.get('reponse-paybox')

    if errorcode is None or errorcode in ('0000', '00001') or not request.GET.get('reference-fun'):
        return HttpResponseBadRequest()

    # We can not retrieve an order from API if it's not validated,
    # therefore we can not tell our user which course the failed to pay for !!

    order_number = request.GET['reference-fun']

    return render_to_response('payment/error.html', {
        'errorcode': errorcode,
        'order_number': order_number,
    })


@csrf_exempt
@login_required
def paybox_cancel(request):
    """User clicked on 'Cancel' before entering card information."""
    if request.GET.get('reponse-paybox') != '00001' or not request.GET.get('reference-fun'):
        return HttpResponseBadRequest()

    order_number = request.GET['reference-fun']

    return render_to_response('payment/cancel.html', {
        'order_number': order_number,
    })
