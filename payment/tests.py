# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import json

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from mock import patch

from student.models import UserProfile
from verify_student.models import SoftwareSecurePhotoVerification

from courses.models import Course
from fun.tests.utils import skipUnlessLms

from .utils import get_course


@override_settings(FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION=False)
@skipUnlessLms
class PayboxSystemViewsTest(TestCase):
    def setUp(self):
        super(PayboxSystemViewsTest, self).setUp()
        self.user = User.objects.create(username='user', first_name='first_name',
                last_name='last_name', email='richard@example.com', is_active=True)
        self.user.set_password('test')
        self.user.save()
        UserProfile.objects.create(user=self.user)
        self.client.login(username=self.user.username, password='test')
        self.course = Course.objects.create(key='FUN/0002/session1', title=u"course title")
        self.params = {
            'amount': '10000',
            'reference-fun': 'FUN-100056',
            'autorisation': 'XXXXXX',
            'reponse-paybox': '',
            'appel-paybox': '16047443',
            'transaction-paybox': '7558206',
        }
        self.api_response = {
            'number': 'FUN-100056',
            'total_excl_tax': '100.00',
            'lines': [
                {
                    'product': {
                        'attribute_values': [
                            {
                                'name': 'course_key',
                                'value': self.course.key
                            }
                        ]
                    }
                }
            ]
        }

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_success(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Paiement réussi", soup.find('h2').text)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_success_wrong_api_return_value(self, get_order_mock):
        get_order_mock.return_value = {}
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(404, response.status_code)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_success_empty_api_return_value(self, get_order_mock):
        get_order_mock.return_value = {
            'lines': []
        }
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(404, response.status_code)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_false_success(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params['reponse-paybox'] = '0000X'
        response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(400, response.status_code)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_success_missing_argument(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params.pop('reponse-paybox')
        response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(400, response.status_code)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_cancel(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params['reponse-paybox'] = '00001'
        response = self.client.get(reverse('payment-cancel'), self.params)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Abandon du paiement", soup.find('h2').text)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_cancel_missing_argument(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params.pop('reponse-paybox')
        response = self.client.get(reverse('payment-cancel'), self.params)
        self.assertEqual(400, response.status_code)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_error(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        errorcode = '00002'
        self.params['reponse-paybox'] = errorcode
        response = self.client.get(reverse('payment-error'), self.params)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Une erreur a eu lieu", soup.find('h2').text)
        self.assertEqual(errorcode, soup.find('strong', class_='errorcode').text)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_error_missing_argument(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        self.params.pop('reponse-paybox')
        response = self.client.get(reverse('payment-error'), self.params)
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
