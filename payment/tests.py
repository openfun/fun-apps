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
        self.params = {
            'amount': '10000',
            'reference-fun': 'EDX-100056',
            'autorisation': 'XXXXXX',
            'reponse-paybox': '',
            'appel-paybox': '16047443',
            'transaction-paybox': '7558206',
        }

    def test_callbackpage_success(self):
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1,
                SoftwareSecurePhotoVerification.objects.filter(user=self.user).count())
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Paiement réussi", soup.find('div', class_='result').text)

    def test_callbackpage_success_already_verified(self):
        SoftwareSecurePhotoVerification.objects.create(
                user=self.user, display=False,
                status='approved', reviewing_user=self.user,
                reviewing_service='created by unit test')
        self.params['reponse-paybox'] = '00000'
        response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1,
                SoftwareSecurePhotoVerification.objects.filter(user=self.user).count())

    def test_callbackpage_false_success(self):
        self.params['reponse-paybox'] = '0000X'
        with self.assertRaises(Exception):
            response = self.client.get(reverse('payment-success'), self.params)
        self.assertEqual(0,
                SoftwareSecurePhotoVerification.objects.filter(user=self.user).count())

    def test_callbackpage_cancel(self):
        self.params['reponse-paybox'] = '00001'
        response = self.client.get(reverse('payment-cancel'), self.params)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Abandon du paiement", soup.find('div', class_='result').text)

    def test_callbackpage_error(self):
        errorcode = '00002'
        self.params['reponse-paybox'] = errorcode
        response = self.client.get(reverse('payment-error'), self.params)
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Une erreur a eu lieu", soup.find('div', class_='result').text)
        self.assertEqual(errorcode, soup.find('div', class_='errorcode').text)

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
