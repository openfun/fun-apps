# -*- coding: utf-8 -*-

# Imports #####################################################################

from mock import patch

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from contact.views import ContactFormView
from fun.tests.utils import skipUnlessLms


@skipUnlessLms
@patch.dict('django.conf.settings.FEATURES', {'ENABLE_CONTACT_FORM': True})
class ContactTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.post_vars = {
            'name': u'John Doe',
            'email': u'john@example.com',
            'phone': u'+33664446505',
            'function': u'student',
            'inquiry': u'account',
            'body': u'Hello! æêé'
        }

    @patch('contact.views.ContactFormView.render_to_response')
    def test_contact_form_view_get(self, mock_render_to_response):
        """
        Test contact page display (GET)
        """
        contact_form_view = ContactFormView.as_view()
        request = self.factory.get(reverse('contact:contact'))
        contact_form_view(request)

        self.assertEqual(len(mock_render_to_response.call_args_list), 1)
        mock_call = mock_render_to_response.call_args_list[0][0]
        self.assertEqual(len(mock_call), 1)
        self.assertEqual(['form'], mock_call[0].keys())
        self.assertEqual(len(mail.outbox), 0)

    @patch('contact.views.ContactFormView.render_to_response')
    def test_contact_form_view_post_missing_fields(self, mock_render_to_response):
        """
        Test contact page display (POST), with missing fields values
        """
        contact_form_view = ContactFormView.as_view()
        request = self.factory.post(reverse('contact:contact'))
        contact_form_view(request)

        self.assertEqual(len(mock_render_to_response.call_args_list), 1)
        mock_call = mock_render_to_response.call_args_list[0][0]
        self.assertEqual(len(mock_call), 1)
        self.assertEqual(['form'], mock_call[0].keys())

        form = mock_call[0]['form']
        self.assertTrue(form.errors['name'])
        self.assertTrue(form.errors['email'])
        self.assertTrue(form.errors['body'])
        self.assertTrue(form.errors['inquiry'])
        self.assertTrue('function' not in form.errors)
        self.assertTrue('phone' not in form.errors)

        self.assertEqual(len(mail.outbox), 0)

    def test_contact_form_view_post_sent(self):
        """
        Test contact page display (POST), all correct & sent
        """
        response = self.client.post(reverse('contact:contact'), self.post_vars)
        self.assertRedirects(response, reverse('contact:contact_form_sent'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Contact', mail.outbox[0].subject)
        self.assertIn('FUN', mail.outbox[0].subject)
        self.assertIn(self.post_vars["name"], mail.outbox[0].body)
        self.assertIn(self.post_vars["email"], mail.outbox[0].body)
        self.assertIn(self.post_vars["phone"], mail.outbox[0].body)
