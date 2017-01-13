# -*- coding: utf-8 -*-

from mock import Mock

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage

from django.test import TestCase
from unittest import skipIf

""""
Warning for now those tests will only work when dummy SMTP server are running:
python -m smtpd -n -c DebuggingServer localhost:1025
python -m smtpd -n -c DebuggingServer localhost:1026
"""


@skipIf(True, "SMTP tests require two running SMTP servers")
class SMTPsTest(TestCase):

    def setUp(self):
        settings.EMAIL_BACKEND = 'fun.smtp.backend.MultipleSMTPEmailBackend'
        settings.EMAIL_HOST = {
            'bulk': {'host': 'localhost', 'port': 1025},
            'transactional': {'host': 'localhost', 'port': 1026}
            }

        self.connection = get_connection()
        self.mock_bulk = Mock(return_value=True)
        self.mock_transactional = Mock(return_value=True)
        self.connection.bulk._send = self.mock_bulk
        self.connection.transactional._send = self.mock_transactional

    def test_simple_transactional(self):
        EmailMessage('subject', 'message', 'transactional@fun-mooc.fr', ['robert@fun.fr'], connection=self.connection).send()
        self.assertEqual(False, self.mock_bulk.called)
        self.assertEqual(True, self.mock_transactional.called)

    def test_simple_bulk(self):
        EmailMessage('subject', 'message', 'xxx-no-reply@fun-mooc.fr', ['robert@fun.fr'], connection=self.connection).send()
        self.assertEqual(True, self.mock_bulk.called)
        self.assertEqual(False, self.mock_transactional.called)

    def test_multiple1(self):
        messages = [EmailMessage('subject', 'message', sender, ['robert@fun.fr'])
                for sender in ['transactional@fun-mooc.fr', 'xxx-no-reply@fun-mooc.fr']]
        self.connection.send_messages(messages)
        self.assertEqual(True, self.mock_bulk.called)
        self.assertEqual(True, self.mock_transactional.called)

    def test_multiple2(self):
        messages = [EmailMessage('subject', 'message', sender, ['robert@fun.fr'])
                for sender in ['transactional1@fun-mooc.fr', 'transactional2@fun-mooc.fr']]
        self.connection.send_messages(messages)
        self.assertEqual(False, self.mock_bulk.called)
        self.assertEqual(True, self.mock_transactional.called)

    def test_multiple3(self):
        messages = [EmailMessage('subject', 'message', sender, ['robert@fun.fr'])
                for sender in ['001-no-reply@fun-mooc.fr', '002-no-reply@fun-mooc.fr']]
        self.connection.send_messages(messages)
        self.assertEqual(True, self.mock_bulk.called)
        self.assertEqual(False, self.mock_transactional.called)
