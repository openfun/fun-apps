# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.decorators import method_decorator

from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_oauth.authentication import OAuth2Authentication

from lms.djangoapps.verify_student.models import SoftwareSecurePhotoVerification

from payment.utils import send_confirmation_email, \
    register_user_verified_cohort, get_order, get_course

from .serializers import PaymentNotificationSerializer

logger = logging.getLogger(__name__)


class PaymentNotificationAPIView(APIView):
    """Call by ecommerce service when receiving Paybox notification of successful transaction.
    We create a dummy PaymentNotificationSerializer object which avoid in edx-platform
    identity verification as we entrusted that to ProcturU. Also send a confirmation email to user.
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)

    @method_decorator(transaction.non_atomic_requests) # Used to add user into cohort
    def dispatch(self, *args, **kwargs):    # pylint: disable=missing-docstring
        return super(PaymentNotificationAPIView, self).dispatch(*args, **kwargs)

    def post(self, request, format=None):
        serializer = PaymentNotificationSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(email=request.data['email'])
            logger.info('Received success notification from ecommerce service for user %s', user.username)
            if not SoftwareSecurePhotoVerification.objects.filter(user=user).exists():
                SoftwareSecurePhotoVerification.objects.create(
                    user=user,
                    display=False,
                    status='approved',
                    reviewing_service='Automatic Paybox',
                )
            order = None
            if settings.FEATURES.get('ENABLE_PAYMENT_FAKE'):
                order = settings.FUN_PAYMENT_FAKE_ORDER(request.data['fun_test_course_key'])
                # Don't send confirmation email when testing
            else:
                order = get_order(user, request.data['order_number'])
                send_confirmation_email(user, order)

            register_user_verified_cohort(user,  order)
            logger.info('Created SoftwareSecurePhotoVerification object and sent FUN confirmation email to user %s',
                    user.username)
            return Response()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


payment_notification = PaymentNotificationAPIView.as_view()
