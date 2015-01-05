# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase, TEST_DATA_DIR

from universities.factories import UniversityFactory


class BaseBackoffice(ModuleStoreTestCase):
    def setUp(self):
        super(BaseBackoffice, self).setUp()
        self.university = UniversityFactory(name='FUN', code='FUN')
        self.backoffice_group = Group.objects.create(name='fun_backoffice')  # create the group
        self.course = CourseFactory(org=self.university.code, number='001', display_name='test')  # create a non published course
        self.user = UserFactory()
        self.list_url = reverse('backoffice-courses-list')


class TestAuthetification(BaseBackoffice):
    def test_auth(self):
        # Users not belonging to `fun_backoffice` should not log in.
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(self.list_url)
        self.assertEqual(302, response.status_code)

        self.user.groups.add(self.backoffice_group)
        self.client.login(username=self.user.username, password='test')
        response = self.client.get(self.list_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.context['courses']))  # use is not staff he can not see not published course
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(self.list_url)
        self.assertEqual(1, len(response.context['courses']))  # OK


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
            'full_name': u"super student",
            'teacher1': u'teacher',
            'title1': u"title",
        }
        response = self.client.post(url, data)
        self.assertEqual('text/pdf', response._headers['content-type'][1])


