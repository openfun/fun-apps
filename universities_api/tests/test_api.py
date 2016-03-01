# -*- coding: utf-8 -*-

import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from student.tests.factories import UserFactory

from fun.tests.utils import skipUnlessLms
from universities.tests.factories import UniversityFactory


@skipUnlessLms
class UniversityAPITest(TestCase):

    def setUp(self):
        self.api_url = reverse('fun-universities-api:universities-list')
        self.user = UserFactory(username='user', password='password') # user with profile
        self.univ_1 = UniversityFactory(code='test-university-1')
        self.univ_2 = UniversityFactory(code='test-university-2')

    def login_as_admin(self):
        self.user.is_staff = True
        self.user.save()
        self.client.login(username='user', password='password')

    def test_course_list_api_response_loads(self):
        self.login_as_admin()
        response = self.client.get(self.api_url)
        data = json.loads(response.content)
        self.assertIn('results', data)

    def test_can_update_university_score_as_admin(self):
        self.login_as_admin()
        self.univ_1.score = 0
        self.univ_1.save()
        data = {'score': 100}
        url = reverse('fun-universities-api:universities-detail',
            args=[self.univ_1.id]
        )
        response = self.client.put(url, data)
        response_data = json.loads(response.content)
        self.assertEqual(100, response_data['score'])

    def test_cannot_update_university_if_set_as_prevent_auto_update(self):
        self.login_as_admin()
        self.univ_1.prevent_auto_update = True
        self.univ_1.save()
        data = {'score': 100}
        url = reverse('fun-universities-api:universities-detail',
            args=[self.univ_1.id]
        )
        response = self.client.put(url, data)
        self.assertNotEqual(response.status_code, 200)

    def test_cannot_update_course_score_if_not_logged_in(self):
        self.client.logout()
        data = {'score': 100}
        url = reverse('fun-universities-api:universities-detail',
            args=[self.univ_1.id]
        )
        response = self.client.put(url, data)
        self.assertNotEqual(response.status_code, 200)
