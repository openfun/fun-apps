# -*- coding: utf-8 -*-

import dateutil.parser
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _
from django.utils import translation

from requests.exceptions import ConnectionError

from edxmako.shortcuts import render_to_string
from student.models import CourseEnrollment

from openedx.core.djangoapps.commerce.utils import ecommerce_api_client

from courses.models import Course

logger = logging.getLogger(__name__)


def get_order(user, order_id):
    try:
        order = ecommerce_api_client(user).orders(order_id).get()
    except ConnectionError as e:
        order = None
        logger.exception(e)
    return order


def get_basket(user, order_id):
    return ecommerce_api_client(user).baskets(order_id).get()


def get_course(order_or_basket):
    """Retrieve course from order or basket product properties."""
    attributes = order_or_basket['lines'][0]['product']['attribute_values']
    course_key = [d['value'] for d in attributes if d['name'] == 'course_key'][0]
    return Course.objects.get(key=course_key)


def get_order_context(user, order, course):
    context = dict()
    context['order'] = order
    context['ordered_course'] = course
    context['user'] = user
    context['total_incl_tax'] = order['total_excl_tax']  # we do not know yet how we will handle taxes in the future...
    return context


def send_confirmation_email(user, order_number):
    order = get_order(user, order_number)
    course = get_course(order)
    subject = _(u"[FUN-MOOC] Payment confirmation")
    context = get_order_context(user, order, course)
    with translation.override(user.profile.language):
        text_content = render_to_string('payment/email/confirmation-email.txt', context)
        html_content = render_to_string('payment/email/confirmation-email.html', context)
    email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.PAYMENT_SUPPORT_EMAIL,
            to=[user.email],
            bcc=[settings.PAYMENT_ADMIN],
        )
    email.attach_alternative(html_content, "text/html")
    email.send()


def format_date_order(order, format):
    return dateutil.parser.parse(order['date_placed']).strftime(format)

