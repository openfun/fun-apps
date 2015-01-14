# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase, TEST_DATA_DIR

from universities.factories import UniversityFactory

from xmodule.modulestore.tests.django_utils import TEST_DATA_MOCK_MODULESTORE

@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class BaseBackoffice(ModuleStoreTestCase):
    def setUp(self):
        super(BaseBackoffice, self).setUp()
        self.university = UniversityFactory(name='FUN', code='FUN')
        self.backoffice_group = Group.objects.create(name='fun_backoffice')  # create the group
        self.course = CourseFactory(org=self.university.code, number='001', display_name='test')  # create a non published course
        self.user = UserFactory()
        self.list_url = reverse('backoffice-courses-list')


class TestAuthetification(BaseBackoffice):
    def test_auth_not_belonging_to_group(self):
        # Users not belonging to `fun_backoffice` should not log in.
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(self.list_url)
        self.assertEqual(302, response.status_code)

    def test_auth_not_staff(self):
        self.user.groups.add(self.backoffice_group)
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(self.list_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context['courses']))  # use is not staff he can not see not published course

    def test_auth_staff(self):
        self.user.groups.add(self.backoffice_group)
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(self.list_url)
        self.assertEqual(1, len(response.context['courses']))  # OK

@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class TestGenerateCertificate(BaseBackoffice):
    def setUp(self):
        super(TestGenerateCertificate, self).setUp()
        self.user.groups.add(self.backoffice_group)
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.user.username, password='test')

    def test_certificate(self):
        url = reverse('backoffice-course-detail', args=[self.course.id.to_deprecated_string()])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = {
            'full_name' : u'superéléve',
            'form-0-full_name': u'pierre',
            'form-0-title' : u'prof',
            'form-1-full_name' : '',
            'form-1-title' : '',
            'form-2-full_name' : '',
            'form-2-title' : '',
            'form-3-full_name' : '',
            'form-3-title' : '',
            'form-INITIAL_FORMS' : 0,
            'form-MAX_NUM_FORMS' : 1000,
            'form-TOTAL_FORMS' : 4,
        }
        response = self.client.post(url, data)
        self.assertEqual('application/pdf', response._headers['content-type'][1])


