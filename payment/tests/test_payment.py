# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from mock import patch
from requests.exceptions import ConnectionError

from student.models import UserProfile
from verify_student.models import SoftwareSecurePhotoVerification

from courses.models import Course, CourseUniversityRelation
from fun.tests.utils import skipUnlessLms
from universities.tests.factories import UniversityFactory

from ..utils import (get_course, send_confirmation_email, get_order_context,
        format_date_order, get_order)


def ecommerce_order_api_response(course_key_string):
    return {
        'number': 'FUN-100056',
        'total_excl_tax': '100.00',
        'date_placed': '2016-03-17T10:07:36Z',
        'lines': [
            {
                'product': {
                    'attribute_values': [
                        {
                            'name': 'course_key',
                            'value': course_key_string,
                        }
                    ]
                }
            }
        ]
    }

ecommerce_basket_api_response = {
    "id": 130,
    "date_created": "2016-04-01T12:32:34Z",
    "lines": [
        {
            "product": {
                "attribute_values": [
                    {
                        "name": "course_key",
                        "value": "FUN/0002/session1"
                    },
                ],
            },
            "price_excl_tax": "100.00",
        }
    ]
}


def ecommerce_api_listing_course(course):
    return {u'count': 0, u'previous': None, u'results': [course] if course else [], u'next': None}


@override_settings(FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION=False)
@skipUnlessLms
class AbstractPaymentTest(TestCase):
    def setUp(self):
        super(AbstractPaymentTest, self).setUp()
        self.user = User.objects.create(username='user', first_name='first_name',
                                        last_name='last_name', email='richard@example.com', is_active=True)
        self.user.set_password('test')
        self.user.save()
        UserProfile.objects.create(user=self.user, language='fr', name=u"Robert Cash")
        self.client.login(username=self.user.username, password='test')
        self.course = Course.objects.create(key='FUN/0002/session1', title=u"course title", )
        self.university = UniversityFactory(name=u"FÛN")
        CourseUniversityRelation.objects.create(
            course=self.course, university=self.university)
        self.api_response = ecommerce_order_api_response(self.course.key)


class PayboxSystemViewsTest(AbstractPaymentTest):
    def setUp(self):
        super(PayboxSystemViewsTest, self).setUp()
        self.params = {
            'amount': '10000',
            'reference-fun': 'FUN-100056',
            'autorisation': 'XXXXXX',
            'reponse-paybox': '',
            'appel-paybox': '16047443',
            'transaction-paybox': '7558206',
        }

    @patch('payment.views.get_order_or_404')
    def test_callback_page_success(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment:success'), self.params)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Paiement réussi", soup.find('h2').text)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_success_wrong_api_return_value(self, get_order_mock):
        get_order_mock.return_value = {}
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment:success'), self.params)
        self.assertEqual(404, response.status_code)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_success_empty_api_return_value(self, get_order_mock):
        get_order_mock.return_value = {
            'lines': []
        }
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment:success'), self.params)
        self.assertEqual(404, response.status_code)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_false_success(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params['reponse-paybox'] = '0000X'
        response = self.client.get(reverse('payment:success'), self.params)
        self.assertEqual(400, response.status_code)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_success_missing_argument(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params.pop('reponse-paybox')
        response = self.client.get(reverse('payment:success'), self.params)
        self.assertEqual(400, response.status_code)

    @patch('payment.views.get_basket_or_404')
    def test_callbackpage_cancel(self, get_order_mock):
        get_order_mock.return_value = ecommerce_basket_api_response
        self.params['reponse-paybox'] = '00001'
        response = self.client.get(reverse('payment:cancel'), self.params)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Abandon du paiement", soup.find('h2').text)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_cancel_missing_argument(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params.pop('reponse-paybox')
        response = self.client.get(reverse('payment:cancel'), self.params)
        self.assertEqual(400, response.status_code)

    @patch('payment.views.get_basket_or_404')
    def test_callbackpage_error(self, get_basket_mock):
        get_basket_mock.return_value = ecommerce_basket_api_response
        errorcode = '00002'
        self.params['reponse-paybox'] = errorcode
        response = self.client.get(reverse('payment:error'), self.params)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Une erreur a eu lieu", soup.find('h2').text)
        self.assertEqual(errorcode, soup.find('strong', class_='errorcode').text)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_error_missing_argument(self, get_basket_mock):
        get_basket_mock.return_value = self.api_response
        self.params.pop('reponse-paybox')
        response = self.client.get(reverse('payment:error'), self.params)
        self.assertEqual(400, response.status_code)

    @patch('payment.utils.get_order')
    def test_payment_notification_api(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        data = {'username': self.user.username,
                'email': self.user.email,
                'order_number': '0'}

        response = self.client.post(reverse('fun-payment-api:payment-notification'),
                                    json.dumps(data),
                                    content_type="application/json")
        self.assertEqual(1,
                         SoftwareSecurePhotoVerification.objects.filter(
                             user=self.user).count())
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(True,
                         mail.outbox[0].message().is_multipart())

    @patch('payment.utils.get_order')
    def test_payment_notification_api_already_verified(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        SoftwareSecurePhotoVerification.objects.create(
            user=self.user, display=False,
            status='approved', reviewing_user=self.user,
            reviewing_service='created by unit test')
        get_order_mock.return_value = self.api_response
        data = {'username': self.user.username,
                'email': self.user.email,
                'order_number': '0'}
        response = self.client.post(reverse('fun-payment-api:payment-notification'),
                                    json.dumps(data),
                                    content_type="application/json")
        self.assertEqual(1,
                         SoftwareSecurePhotoVerification.objects.filter(
                             user=self.user).count())
        self.assertEqual(1, len(mail.outbox))

    def test_utils_get_course(self):
        self.assertEqual(self.course,
                         get_course(self.api_response))

    @patch('payment.utils.get_order')
    def test_confirmation_email_language(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        send_confirmation_email(self.user, 'FUN-100056')
        self.assertEqual(1, len(mail.outbox))
        soup = BeautifulSoup(mail.outbox[0].message().as_string())
        # default user's language is fr
        self.assertEqual(u"Confirmation de paiement",
                         soup.find('h1', class_='title').text.strip())
        # create new user, with language en
        mail.outbox = []
        user_en = User.objects.create(username='user_en', first_name='first_name',
                                      last_name='last_name', email='richard@example.co.uk', is_active=True)
        UserProfile.objects.create(user=user_en, language='en')
        send_confirmation_email(user_en, 'FUN-100056')
        soup = BeautifulSoup(mail.outbox[0].message().as_string())
        self.assertEqual(u"Payment confirmation",
                         soup.find('h1', class_='title').text.strip())

    @patch('payment.utils.get_order')
    def test_confirmation_email_bill(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        send_confirmation_email(self.user, 'FUN-100056')
        self.assertEqual(1, len(mail.outbox))
        soup = BeautifulSoup(mail.outbox[0].message().as_string())
        self.assertEqual(self.course.title,
                         soup.find('span', class_='line-1-course-title').text.strip())
        self.assertEqual(1,
                         int(soup.find('span', class_='line-1-quantity').text.strip()))
        self.assertEqual(self.university.name,
                         soup.find('span', class_='line-1-course-university').text.strip())
        self.assertEqual(self.user.profile.name,
                         soup.find('span', class_='user-full-name').text.strip())


class PaymentUtilsTest(AbstractPaymentTest):
    def test_date_format(self):
        date = u"2016-03-24T11:11:09Z"
        order = {"date_placed": date}
        date1 = format_date_order(order, "%m/%d/%y")
        date2 = format_date_order(order, "%d/%m/%y")

        self.assertEqual(date1, "03/24/16")
        self.assertEqual(date2, "24/03/16")

    def test_get_order_context(self):
        order = {"total_excl_tax": 123}
        course = "cours"
        user = self.user
        context = get_order_context(user, order, course)

        self.assertEqual(order, context['order'])
        self.assertEqual(course, context['ordered_course'])
        self.assertEqual(user, context['user'])
        self.assertEqual(order['total_excl_tax'], context['total_incl_tax'])


class GetOrderTest(AbstractPaymentTest):
    @patch('slumber.Resource.get')
    def test_get_order_ok(self, api_mock):
        api_mock.return_value = self.api_response
        order = get_order(self.user, "FUN-100056")

        self.assertEqual(self.api_response, order)

    @patch('slumber.Resource.get')
    def test_get_order_connection_error(self, api_mock):
        api_mock.side_effect = ConnectionError
        order = get_order(self.user, "FUN-100056")

        self.assertEqual(None, order)


class FacturationViewsTest(AbstractPaymentTest):
    @patch("payment.views.get_order")
    def test_detail_receipt_ok(self, patch_get_order):
        patch_get_order.return_value = self.api_response
        order_id = "FUN-100056"
        response = self.client.get(reverse('payment:detail-receipt', kwargs={"order_id": order_id}))
        soup = BeautifulSoup(response.content)

        self.assertEqual(u"Reçu : {}".format(order_id), soup.find("h1").text)
        self.assertIn(u"course title",
                      soup.find("span", {"class": "course-display-name"}).text)

    @patch("payment.views.get_order")
    def test_detail_receipt_with_connection_error(self, patch_get_order):
        patch_get_order.return_value = None
        order_id = "FUN-100056"
        response = self.client.get(reverse('payment:detail-receipt', kwargs={"order_id": order_id}))
        soup = BeautifulSoup(response.content)

        self.assertEqual(u"Reçu : FUN-100056", soup.find("h1").text)
        self.assertIn(u"Une erreur a eu lieu, veuillez ré-essayer plus tard.",
                      soup.find("div", {"class": "order-error"}).text)

    @patch('slumber.Resource.get')
    def test_list_receipt_1_course(self, api_mock):
        api_mock.return_value = ecommerce_api_listing_course(self.api_response)
        response = self.client.get(reverse('payment:list-receipts'))
        soup = BeautifulSoup(response.content)

        self.assertEqual(self.api_response["number"],
                         soup.find("td", {"class": "order_id"}).text)
        self.assertEqual(u"{p} €".format(p=self.api_response["total_excl_tax"]),
                         soup.find("td", {"class": "order_price"}).text)
        self.assertEqual(format_date_order(self.api_response, "%d/%m/%y"),
                         soup.find("td", {"class": "order_date"}).text)

    @patch('slumber.Resource.get')
    def test_list_receipt_with_connection_error(self, api_mock):
        api_mock.side_effect = ConnectionError
        response = self.client.get(reverse('payment:list-receipts'))
        soup = BeautifulSoup(response.content)

        self.assertIn(u"Une erreur a eu lieu, veuillez ré-essayer plus tard.",
                      soup.find("p", {"class": "order-error"}).text)

    @patch('slumber.Resource.get')
    def test_list_receipt_no_course(self, api_mock):
        api_mock.return_value = ecommerce_api_listing_course(None)
        response = self.client.get(reverse('payment:list-receipts'))
        soup = BeautifulSoup(response.content)

        self.assertIn(u"Vous n'avez pas encore souscrit à un examen certifiant.",
                soup.find("p", {"class": "order-empty"}).text)
