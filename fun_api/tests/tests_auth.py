# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class APIAuthTest(TestCase):

    def setUp(self):
        self.get_token_url = reverse('fun-api:get-token')
        self.user = User.objects.create_user(
            username='user', password='password',
        )
        self.user_data = {'username': 'user', 'password': 'password'}

    def test_cannot_get_token_if_not_active(self):
        self.user.is_active = False
        self.user.is_staff = True
        self.user.save()
        response = self.client.post(self.get_token_url, self.user_data)
        self.assertNotEqual(response.status_code, 200)

    def test_cannot_get_token_if_not_staff(self):
        self.user.is_active = True
        self.user.is_staff = False
        self.user.save()
        response = self.client.post(self.get_token_url, self.user_data)
        self.assertNotEqual(response.status_code, 200)

    def test_can_get_token_if_staff(self):
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()
        response = self.client.post(self.get_token_url, self.user_data)
        self.assertContains(response, 'token')

    def test_can_get_token_if_superuser(self):
        self.user.is_active = True
        self.user.is_staff = False
        self.user.is_superuser = True
        self.user.save()
        response = self.client.post(self.get_token_url, self.user_data)
        self.assertContains(response, 'token')
