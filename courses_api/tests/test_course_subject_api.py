# -*- coding: utf-8 -*-

import json
from random import randint

from django.test import TestCase

from student.tests.factories import UserFactory

from fun.tests.utils import skipUnlessLms

from courses.models import CourseSubject
from courses.tests.factories import CourseSubjectFactory


@skipUnlessLms
class CourseSubjectAPITest(TestCase):

    # Read
    ######################

    def test_course_subject_read_detail_anonymous(self):
        """
        Anonymous users should be able to read a course subject detail.
        """
        subject = CourseSubjectFactory()
        response = self.client.get('/fun/api/course_subjects/{:d}/'.format(subject.id))
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.maxDiff = None
        self.assertEqual(content, {
            'name': subject.name, 'short_name': subject.short_name,
            'image': 'http://testserver{:s}'.format(subject.image.url),
            'featured': subject.featured, 'score': subject.score, 'id': subject.id,
            'description': subject.description})

    def test_course_subject_read_detail_user_or_staff(self):
        """
        Any user, staff or not, should be able to read a subject detail.
        """
        subject = CourseSubjectFactory()
        for user in [UserFactory(), UserFactory(is_staff=True)]:
            self.client.login(username=user.username, password='test')
            response = self.client.get('/fun/api/course_subjects/{:d}/'.format(subject.id))
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(content, {
                'name': subject.name, 'short_name': subject.short_name,
                'image': 'http://testserver{:s}'.format(subject.image.url),
                'featured': subject.featured, 'score': subject.score, 'id': subject.id,
                'description': subject.description})

    def test_course_subject_read_list_anonymous(self):
        """
        Anonymous users should be able to read the list of course subjects.
        Results should be ordered by decreasing score first, then by increasing name,
        then by increasing id.
        """
        subject1 = CourseSubjectFactory(score=1, name=u'Aztèques')
        subject2 = CourseSubjectFactory(score=2)
        subject3 = CourseSubjectFactory(score=1, name=u'Algèbre')
        subject4 = CourseSubjectFactory(score=1, name=u'Aztèques')
        subject5 = CourseSubjectFactory(score=1, name=u'Algèbre')
        response = self.client.get('/fun/api/course_subjects/')
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(len(content['results']), 5)
        self.assertEqual(content['results'][0]['name'], subject2.name)
        self.assertEqual(unicode(content['results'][1]['name']), subject3.name)
        self.assertEqual(content['results'][2]['name'], subject5.name)
        self.assertEqual(content['results'][3]['name'], subject1.name)
        self.assertEqual(content['results'][4]['name'], subject4.name)

    def test_course_subject_read_list_user_or_staff(self):
        """
        Any user, staff or not, should be able to read the list of course subjects.
        """
        nb = randint(1, 3)
        CourseSubjectFactory.create_batch(nb)
        for user in [UserFactory(), UserFactory(is_staff=True)]:
            self.client.login(username=user.username, password='test')
            response = self.client.get('/fun/api/course_subjects/')
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(len(content['results']), nb)
            # The object returned should have all 7 fields
            self.assertEqual(len(content['results'][0]), 7)

    # Create
    ######################

    def test_course_subject_create_anonymous(self):
        """
        Anonymous users should not have the possibility to create a course subject
        through the API. A 405 code is returned (and not 403) because the functionnality is
        not just forbidden by not even available.
        """
        data = json.dumps({'name': 'my-name'})
        response = self.client.post(
            '/fun/api/course_subjects/', data, content_type='application/json')
        self.assertEqual(response.status_code, 405)
        self.assertFalse(CourseSubject.objects.exists())

    def test_course_subject_create_user_or_staff(self):
        """
        Authenticated users, even staff, should not have the possibility to create a course
        subject through the API. A 405 code is returned (and not 403) because the functionnality
        is not just forbidden by not even available.
        """
        for user in [UserFactory(), UserFactory(is_staff=True)]:
            self.client.login(username=user.username, password='test')
            data = json.dumps({'name': 'my-name'})
            response = self.client.post(
                '/fun/api/course_subjects/', data, content_type='application/json')
            self.assertEqual(response.status_code, 405)
            self.assertFalse(CourseSubject.objects.exists())

    # Update
    ######################

    def test_course_subject_update_anonymous(self):
        """
        Anonymous users should not have the possibility to update a subject
        through the API. A 405 code is returned (and not 403) because the
        functionnality is not just forbidden by not even available.
        """
        subject = CourseSubjectFactory(score=11)
        data = json.dumps({'score': randint(0, 100)})
        response = self.client.put(
            '/fun/api/course_subjects/{:d}/'.format(subject.id), data,
            content_type='application/json')
        self.assertEqual(response.status_code, 405)
        subject.refresh_from_db()
        self.assertEqual(subject.score, 11)

    def test_course_subject_update_user(self):
        """
        Authenticated users, event staff, should not have the possibility to update a
        course subject through the API. A 405 code is returned (and not 403) because
        the functionnality is not just forbidden by not even available.
        """
        for user in [UserFactory(), UserFactory(is_staff=True)]:
            self.client.login(username=user.username, password='test')
            subject = CourseSubjectFactory(score=11)
            data = json.dumps({'score': randint(0, 100)})
            response = self.client.put(
                '/fun/api/course_subjects/{:d}/'.format(subject.id), data,
                content_type='application/json')
            self.assertEqual(response.status_code, 405)
            subject.refresh_from_db()
            self.assertEqual(subject.score, 11)

    # Delete
    ######################

    def test_course_subject_delete_anonymous(self):
        """
        Anonymous users should not be allowed to delete a course subject through the API.
        A 405 code is returned (and not 403) because the functionnality is not
        just forbidden by not even available.
        """
        subject = CourseSubjectFactory()
        response = self.client.delete('/fun/api/course_subjects/{:d}/'.format(subject.id))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(CourseSubject.objects.filter(id=subject.id).exists())

    def test_course_subject_delete_user(self):
        """
        Authenticated users, even staff, should not have the possibility to delete a course subject
        through the API. A 405 code is returned (and not 403) because the functionnality is not
        just forbidden by not even available.
        """
        for user in [UserFactory(), UserFactory(is_staff=True)]:
            self.client.login(username=user.username, password='test')
            subject = CourseSubjectFactory()
            response = self.client.delete('/fun/api/course_subjects/{:d}/'.format(subject.id))
            self.assertEqual(response.status_code, 405)
            self.assertTrue(CourseSubject.objects.filter(id=subject.id).exists())
