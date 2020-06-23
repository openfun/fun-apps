# -*- coding: utf-8 -*-
"""
Fake payment page for use in acceptance tests.
This view is enabled in the URLs by the feature flag `ENABLE_PAYMENT_FAKE`.

Note that you will still need to configure this view as the payment
processor endpoint in order for the shopping cart to use it:

    settings.CC_PROCESSOR['CyberSource']['PURCHASE_ENDPOINT'] = "/payment/fun_payment_fake"

You can configure the payment to indicate success or failure by sending a PUT
request to the view with param "success"
set to "success" or "failure".  The view defaults to payment success.
"""
import json

import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment
from courses.models import Course


class PaymentFakeView(View):
    """
    Fake payment page for use in acceptance tests.
    """

    # We store the payment status to respond with in a class
    # variable.  In a multi-process Django app, this wouldn't work,
    # since processes don't share memory.  Since Lettuce
    # runs one Django server process, this works for acceptance testing.
    PAYMENT_STATUS_RESPONSE = "success"

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        """
        Disable CSRF for these methods.
        """
        return super(PaymentFakeView, self).dispatch(*args, **kwargs)

    def post(self, request):
        """
        Render a fake payment page.

        This is an HTML form that:

        * Triggers a POST to `postpay_callback()` on submit.

        * Has hidden fields for all the data CyberSource sends to the callback.
            - Most of this data is duplicated from the request POST params (e.g. `amount`)
            - Other params contain fake data (always the same user name and address.
            - Still other params are calculated (signatures)

        * Serves an error page (HTML) with a 200 status code
          if the signatures are invalid.  This is what CyberSource does.

        Since all the POST requests are triggered by HTML forms, this is
        equivalent to the CyberSource payment page, even though it's
        served by the shopping cart app.
        """
        # Here we trigger the notification to the payment API (we skipp the ECOMMERCE PART)
        course_key = request.POST.get('merchant_defined_data1')
        order_fake = settings.FUN_PAYMENT_FAKE_ORDER(course_key)

        self.mock_ecommerce_callbacks(request, course_key, order_fake)

        return render_to_response('payment/success.html', {
            'order': order_fake,
            'ordered_course':  course_key,
        })

    def mock_ecommerce_callbacks(self, request, course_key, order_fake):
        s = requests.Session()
        # First we trigger the notification to the payment API
        data = {'username': request.user.username,
                'email': request.user.email,
                'order_number': order_fake.get('number'),
                'fun_test_course_key': course_key
                # Additional key so to retrieve the course ID.
                }

        path = reverse('fun-payment-api:payment-notification')
        post_url = '{}://{}:{}{}'.format(
            request.environ.get('wsgi.url_scheme'),
            'localhost',
            request.environ.get('SERVER_PORT'),
            path)

        headers = {
            'X-CSRFToken': request.COOKIES.get('csrftoken')
        }
        s.post(post_url, json=data, cookies=request.COOKIES, headers=headers)

        # Secondly we trigger the course enrollment in verified mode
        # This should normally done via a callback from ecommerce to edX
        # through 'commerce_api:v1:courses:retrieve_update' or the v0 equivalent
        edx_course_key = CourseKey.from_string(course_key)
        enrollment = CourseEnrollment.get_enrollment(request.user,
                                                     course_key=edx_course_key)
        if enrollment:
            enrollment.update_enrollment(is_active=True, mode='verified')
            enrollment.save()
