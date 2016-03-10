# -*- coding: utf-8 -*-

import logging

from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authentication import OAuth2Authentication, SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from verify_student.models import SoftwareSecurePhotoVerification

from payment.utils import send_confirmation_email

from .serializers import PaymentNotificationSerializer

logger = logging.getLogger(__name__)


class PaymentNotificationAPIView(APIView):
    """Call by ecommerce service when receiving Paybox notification of successful transaction.
    We create a dummy PaymentNotificationSerializer object which avoid in edx-platform
    identity verification as we entrusted that to ProcturU. Also send a confirmation email to user.
    """
    authentication_classes = (OAuth2Authentication, SessionAuthentication)

    def post(self, request, format=None):
        serializer = PaymentNotificationSerializer(data=request.DATA)
        if serializer.is_valid():
            user = User.objects.get(email=request.DATA['email'])
            logger.info('Received success notification from ecommerce service for user %s', user.username)
            if not SoftwareSecurePhotoVerification.objects.filter(user=user).exists():
                verif = SoftwareSecurePhotoVerification.objects.create(
                        user=user,
                        display=False,
                        status='approved',
                        reviewing_service='Automatic Paybox',)

            send_confirmation_email(user, request.DATA['order_number'])
            logger.info('Created SoftwareSecurePhotoVerification object and sent FUN confirmation email to user %s',
                    user.username)
            return Response()

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


payment_notification = PaymentNotificationAPIView.as_view()
