# -*- coding: utf-8 -*-


from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import sanitize_address

"""SMTP backend which will route emails to differents SMTP backers (and SMTP servers)
regarding from_email field.
If BULK_EMAIL_DEFAULT_FROM_EMAIL is contained in from_email, the email will
be routed to bulk server.

It can be easily tested by running fake Python SMTP servers

EMAIL_BACKEND = 'fun.smtp.backend.CINESMultipleSMTPEmailBackend'
EMAIL_HOST = {
    'bulk': {'host': 'localhost', 'port': 1025},
    'transactional': {'host': 'localhost', 'port': 1026}
    }

python -m smtpd -n -c DebuggingServer localhost:1025
python -m smtpd -n -c DebuggingServer localhost:1026

"""

class MultipleSMTPEmailBackend(BaseEmailBackend):
    def __init__(self, host=None, fail_silently=False, **kwargs):
        super(MultipleSMTPEmailBackend, self).__init__(fail_silently=fail_silently)

        self.bulk = EmailBackend(host=settings.EMAIL_HOST['bulk']['host'],
                port=settings.EMAIL_HOST['bulk']['port'],
                fail_silently=fail_silently, **kwargs)
        self.transactional = EmailBackend(host=settings.EMAIL_HOST['transactional']['host'],
                port=settings.EMAIL_HOST['transactional']['port'],
                fail_silently=fail_silently, **kwargs)

    def open(self):
        return self.bulk.open() and self.transactional.open()

    def close(self):
        self.bulk.close()
        self.transactional.close()

    def split_messages(self, email_messages):
        """Split messages list to send in 2 groups regarding their from_email field."""
        bulk, transactional = [], []
        for message in email_messages:
            from_email = sanitize_address(message.from_email, message.encoding)
            if settings.BULK_EMAIL_DEFAULT_FROM_EMAIL in from_email:
                bulk.append(message)
            else:
                transactional.append(message)
        return bulk, transactional

    def send_messages(self, email_messages):
        bulk_messages, transactional_messages = self.split_messages(email_messages)

        return ((self.bulk.send_messages(bulk_messages) or 0)
                + (self.transactional.send_messages(transactional_messages) or 0))
