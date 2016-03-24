# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from datetime import datetime
import json

from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from mock import patch

from student.models import UserProfile
from verify_student.models import SoftwareSecurePhotoVerification

from courses.models import Course, CourseUniversityRelation
from fun.tests.utils import skipUnlessLms
from universities.tests.factories import UniversityFactory

from .utils import get_course, send_confirmation_email


@override_settings(FUN_ECOMMERCE_DEBUG_NO_NOTIFICATION=False)
@skipUnlessLms
class PayboxSystemViewsTest(TestCase):
    def setUp(self):
        super(PayboxSystemViewsTest, self).setUp()
        self.user = User.objects.create(username='user', first_name='first_name',
                last_name='last_name', email='richard@example.com', is_active=True)
        self.user.set_password('test')
        self.user.save()
        UserProfile.objects.create(user=self.user, language='fr', name=u"Robert Cash")
        self.client.login(username=self.user.username, password='test')
        self.course = Course.objects.create(key='FUN/0002/session1', title=u"course title",)
        self.university = UniversityFactory(name=u"FÛN")
        CourseUniversityRelation.objects.create(
                course=self.course, university=self.university)

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
            'date_placed': '2016-03-17T10:07:36Z',
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
