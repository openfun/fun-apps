# -*- coding: utf-8 -*-

import json
from random import randint

from django.test import TestCase

from student.tests.factories import UserFactory

from fun.tests.utils import skipUnlessLms

from ..models import University
from .factories import UniversityFactory


@skipUnlessLms
class UniversityAPITest(TestCase):

    # Read
    ######################

    def test_universities_read_detail_anonymous(self):
        """
        Anonymous users should be able to read a university detail with
        less fields.
        """
        university = UniversityFactory()
        response = self.client.get('/fun/api/universities/{:d}/'.format(university.id))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {
            'id': university.id, 'name': university.name, 'code': university.code,
            'logo': u'http://testserver{:s}'.format(university.logo.url),
            'banner': u'http://testserver{:s}'.format(university.banner.url)})

    def test_universities_read_detail_user(self):
        """
        Any user should be able to read a university detail with
        less fields.
        """
        user = UserFactory()
        university = UniversityFactory()
        self.client.login(username=user.username, password='test')
        response = self.client.get('/fun/api/universities/{:d}/'.format(university.id))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {
            'id': university.id, 'name': university.name, 'code': university.code,
            'logo': u'http://testserver{:s}'.format(university.logo.url),
            'banner': u'http://testserver{:s}'.format(university.banner.url)})

    def test_universities_read_detail_staff(self):
        """
        Staff users should be able to read a university detail with
        more fields.
        """
        university = UniversityFactory()
        user = UserFactory(is_staff=True)
        self.client.login(username=user.username, password='test')
        response = self.client.get('/fun/api/universities/{:d}/'.format(university.id))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {
            'id': university.id, 'name': university.name, 'code': university.code,
            'logo': u'http://testserver{:s}'.format(university.logo.url),
            'banner': u'http://testserver{:s}'.format(university.banner.url),
            'partnership_level': university.partnership_level,
            'prevent_auto_update': university.prevent_auto_update, 'score': university.score})

    def test_universities_read_list_anonymous(self):
        """
        Anonymous users should be able to read the list of universities:
        Results should be ordered by decreasing score first, then by increasing id.
        """
        university1 = UniversityFactory(score=1)
        university2 = UniversityFactory(score=2)
        university3 = UniversityFactory(score=1)
        response = self.client.get('/fun/api/universities/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content['results']), 3)
        # Results should be ordered as expected
        self.assertEqual(content['results'][0]['name'], university2.name)
        self.assertEqual(content['results'][1]['name'], university1.name)
        self.assertEqual(content['results'][2]['name'], university3.name)
        # The score field should be hidden
        self.assertNotIn('score', content['results'][0])
        self.assertNotIn('score', content['results'][1])
        self.assertNotIn('score', content['results'][2])

    def test_universities_read_list_user(self):
        """
        Authenticated users should be able to read the list of universities.
        Less fields are shown.
        """
        nb = randint(1, 3)
        UniversityFactory.create_batch(nb)
        user = UserFactory()
        self.client.login(username=user.username, password='test')
        response = self.client.get('/fun/api/universities/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content['results']), nb)
        # We expect only 5 fields of the simplified serializer to be shown
        self.assertEqual(len(content['results'][0]), 5)

    def test_universities_read_list_staff(self):
        """
        Staff users should be able to read the list of universities.
        More fields are shown.
        """
        nb = randint(1, 3)
        UniversityFactory.create_batch(nb)
        user = UserFactory(is_staff=True)
        self.client.login(username=user.username, password='test')
        response = self.client.get('/fun/api/universities/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content['results']), nb)
        # We expect all 8 fields to be shown
        self.assertEqual(len(content['results'][0]), 8)

    # Create
    ######################

    def test_universities_create_anonymous(self):
        """
        Anonymous users should not be allowed to create a university
        through the API.
        """
        data = json.dumps({'name': 'my-name'})
        response = self.client.post(
            '/fun/api/universities/', data, content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertFalse(University.objects.exists())

    def test_universities_create_user(self):
        """
        Authenticated users should not be allowed to create a university
        through the API.
        """
        user = UserFactory()
        self.client.login(username=user.username, password='test')
        data = json.dumps({'name': 'my-name'})
        response = self.client.post(
            '/fun/api/universities/', data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(University.objects.exists())

    def test_universities_create_staff(self):
        """
        Staff users should not be allowed to create a university
        through the API.
        """
        user = UserFactory()
        self.client.login(username=user.username, password='test')
        data = json.dumps({'name': 'my-name'})
        response = self.client.post(
            '/fun/api/universities/', data, content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(University.objects.exists())

    # Update
    ######################

    def test_universities_update_anonymous(self):
        """
        Anonymous users should not be allowed to update a university
        through the API.
        """
        university = UniversityFactory(score=11, prevent_auto_update=False)
        data = json.dumps({'score': randint(0, 100)})
        response = self.client.put(
            '/fun/api/universities/{:d}/'.format(university.id), data,
            content_type='application/json')
        self.assertEqual(response.status_code, 401)
        university.refresh_from_db()
        self.assertEqual(university.score, 11)

    def test_universities_update_user(self):
        """
        Authenticated users should not be allowed to update a university
        through the API.
        """
        user = UserFactory()
        self.client.login(username=user.username, password='test')
        university = UniversityFactory(score=11, prevent_auto_update=False)
        data = json.dumps({'score': randint(0, 100)})
        response = self.client.put(
            '/fun/api/universities/{:d}/'.format(university.id), data,
            content_type='application/json')
        self.assertEqual(response.status_code, 403)
        university.refresh_from_db()
        self.assertEqual(university.score, 11)

    def test_universities_update_staff(self):
        """
        Staff users should be able to update only the "score" field of a university
        through the API.
        """
        user = UserFactory(is_staff=True)
        self.client.login(username=user.username, password='test')
        university = UniversityFactory(
            name=u'old university', code=u'uni-old', partnership_level='level-1',
            prevent_auto_update=False, score=11, logo='logo_old.jpg', banner='banner_old.jpg')

        # For each field, let's define a value different from the value on the university
        # we just created. In the following we will try to update the university through the
        # API with these values, and make sure it only works for the "score" field.
        new_values = {
            'name': u'new university', 'code': u'uni-new', 'partnership_level': u'level-2',
            'prevent_auto_update': True, 'score': 12, 'logo': 'logo_new.jpg',
            'banner': 'banner_new.jpg'}

        # Try updating the existing university one field at a time for each field
        for field, new_value in new_values.items():
            old_value = getattr(university, field)
            # Make a PUT on the API with the new value for the field
            data = json.dumps({field: new_value})
            response = self.client.put(
                '/fun/api/universities/{:d}/'.format(university.id), data,
                content_type='application/json')
            self.assertEqual(response.status_code, 200)
            # Check that the value is only updated on the object for the "score" field
            university.refresh_from_db()
            if field == 'score':
                self.assertEqual(university.score, new_value)
            else:
                self.assertEqual(getattr(university, field), old_value)

    def test_universities_update_staff_prevent_auto_update(self):
        """
        Staff users should not be allowed to change the "score" of a university
        through the API when the "auto_prevent_update" flag is set.
        """
        user = UserFactory(is_staff=True)
        self.client.login(username=user.username, password='test')
        university = UniversityFactory(score=11, prevent_auto_update=True)
        new_score = randint(0, 100)
        data = json.dumps({'score': new_score})
        response = self.client.put(
            '/fun/api/universities/{:d}/'.format(university.id), data,
            content_type='application/json')
        self.assertEqual(response.status_code, 403)
        university.refresh_from_db()
        self.assertEqual(university.score, 11)

    # Delete
    ######################

    def test_universities_delete_anonymous(self):
        """
        Anonymous users should not be allowed to delete a university through the API.
        """
        university = UniversityFactory()
        response = self.client.delete('/fun/api/universities/{:d}/'.format(university.id))
        self.assertEqual(response.status_code, 401)
        self.assertTrue(University.objects.filter(id=university.id).exists())

    def test_universities_delete_user(self):
        """
        Authenticated users should not be allowed to delete a university through the API.
        """
        user = UserFactory()
        self.client.login(username=user.username, password='test')
        university = UniversityFactory()
        response = self.client.delete('/fun/api/universities/{:d}/'.format(university.id))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(University.objects.filter(id=university.id).exists())

    def test_universities_delete_staff(self):
        """
        Staff users should not have the possibility to delete a university through the API.
        """
        user = UserFactory(is_staff=True)
        self.client.login(username=user.username, password='test')
        university = UniversityFactory()
        response = self.client.delete('/fun/api/universities/{:d}/'.format(university.id))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(University.objects.filter(id=university.id).exists())
