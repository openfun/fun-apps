# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.utils import translation

from edxmako.shortcuts import render_to_string

from commerce import ecommerce_api_client

from courses.models import Course


def get_order(user, order_id):
    return ecommerce_api_client(user).orders(order_id).get()


def get_course(order):
    attributes = order['lines'][0]['product']['attribute_values']
    course_key = [d['value'] for d in attributes if d['name'] == 'course_key'][0]
    return Course.objects.get(key=course_key)


def send_confirmation_email(user, order_number):
    order = get_order(user, order_number)
    course = get_course(order)
    context = {}
    context['order'] = order
    context['course'] = course
    context['user'] = user
    context['total_incl_tax'] = order['total_excl_tax']  # we do not know yet how we will handle taxes in the future...
    subject = _(u"[FUN-MOOC] Payment confirmation")
    with translation.override(user.profile.language):
        text_content = render_to_string('payment/email/confirmation-email.txt', context)
        html_content = render_to_string('payment/email/confirmation-email.html', context)
    email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.PAYMENT_SUPPORT_EMAIL,
            to=[user.email, settings.PAYMENT_ADMIN],
        )
    email.attach_alternative(html_content, "text/html")
    email.send()
