# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase
from django.test.utils import override_settings

from mock import call, patch

from student.models import UserProfile
from verify_student.models import SoftwareSecurePhotoVerification

from courses.models import Course
from fun.tests.utils import skipUnlessLms


@override_settings(FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION=False)
@skipUnlessLms
class PayboxSystemViewsTest(TestCase):
    def setUp(self):
        super(PayboxSystemViewsTest, self).setUp()
        self.user = User.objects.create(username='user', first_name='first_name',
                last_name='last_name', is_active=True)
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
            'total_excl_tax': '10000',
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
        self.assertEqual(1,
                SoftwareSecurePhotoVerification.objects.filter(user=self.user).count())
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Paiement réussi", soup.find('h2').text)

    @patch('payment.views.get_order_or_404')
    def test_callbackpage_success_already_verified(self, get_order_mock):
        get_order_mock.return_value = self.api_response
        SoftwareSecurePhotoVerification.objects.create(
                user=self.user, display=False,
                status='approved', reviewing_user=self.user,
                reviewing_service='created by unit test')
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1,
                SoftwareSecurePhotoVerification.objects.filter(user=self.user).count())

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
        self.assertEqual(0,
                SoftwareSecurePhotoVerification.objects.filter(user=self.user).count())

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

    @patch('payment.views.requests')
    def test_ecommerce_proxy_notification(self, mock_requests):
        mock_requests.post.return_value.status_code = 200
        errorcode = '00000'
        self.params['reponse-paybox'] = errorcode
        qd = QueryDict('', mutable=True)
        qd.update(self.params)
        response = self.client.post(reverse('payment-notification'), self.params)
        self.assertEqual(200, response.status_code)
        self.assertEqual(mock_requests.post.call_args_list,
                [call(settings.ECOMMERCE_NOTIFICATION_URL, qd)])
