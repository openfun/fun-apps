# -*- coding: utf-8 -*-

import csv
from StringIO import StringIO

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from lang_pref import LANGUAGE_KEY
from openedx.core.djangoapps.user_api.preferences.api import set_user_preference
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from student.models import UserProfile
from universities.factories import UniversityFactory

from ..models import Course, Teacher


class BaseTestCase(ModuleStoreTestCase):
    def setUp(self):
        self.password = super(BaseTestCase, self).setUp()
        self.course = None
        self.backoffice_group = None

    def init(self, is_superuser, university_code):
        self.backoffice_group, _created = Group.objects.get_or_create(name='fun_backoffice')
        self.user.is_staff = False
        self.user.is_superuser = is_superuser
        self.user.save()
        UserProfile.objects.create(user=self.user)
        self.course = CourseFactory.create(org=university_code)

    def login(self):
        self.client.login(username=self.user.username, password=self.password)


class BaseBackoffice(BaseTestCase):
    def setUp(self):
        super(BaseBackoffice, self).setUp()
        self.university = UniversityFactory.create()
        self.init(False, self.university.code)
        self.list_url = reverse('backoffice:courses-list')

    def login_with_backoffice_group(self):
        self.user.groups.add(self.backoffice_group)
        self.login()


class BaseCourseDetail(BaseTestCase):
    def setUp(self):
        super(BaseCourseDetail, self).setUp()
        self.init(True, "fun")

        self.user.groups.add(self.backoffice_group)
        set_user_preference(self.user, LANGUAGE_KEY, 'en-en')
        self.client.login(username=self.user.username, password=self.password)
        self.url = reverse('backoffice:course-detail', args=[self.course.id.to_deprecated_string()])


class TestAuthentication(BaseBackoffice):
    def test_users_not_belonging_to_group_should_not_login(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.list_url)
        self.assertEqual(302, response.status_code)

    def test_users_belonging_to_group_should_login_and_see_no_published_course(self):
        self.login_with_backoffice_group()
        response = self.client.get(self.list_url)
        self.assertEqual(200, response.status_code)
        # user is not staff so he cannot see any published course
        self.assertEqual(0, len(response.context['course_infos']))

    def test_staff_users_see_all_courses(self):
        self.user.groups.add(self.backoffice_group)
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.list_url)
        self.assertEqual(1, len(response.context['course_infos']))


class TestGenerateCertificate(BaseBackoffice):
    def setUp(self):
        super(TestGenerateCertificate, self).setUp()
        self.login_with_backoffice_group()

    def test_certificate(self):
        url = reverse('backoffice:generate-test-certificate', args=[self.course.id.to_deprecated_string()])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = {
            'full_name' : u'super élève',
        }
        response = self.client.post(url, data)
        self.assertEqual('application/pdf', response._headers['content-type'][1])


class TestDeleteCourse(BaseCourseDetail):
    def test_get_view(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_funcourse_automatique_creation(self):
        """A fun Course object should be automaticaly created if it do not already exists."""
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, Course.objects.filter(key=self.course.id.to_deprecated_string()).count())

    def test_delete_course(self):
        data = {'action': 'delete-course'}
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(None, modulestore().get_course(self.course.id))
        self.assertEqual(0, Course.objects.filter(key=self.course.id.to_deprecated_string()).count())
        self.assertIn(_(u"Course <strong>%s</strong> has been deleted.") % self.course.id,
                      response.content.decode('utf-8'))

    def test_no_university(self):
        """In a course is not bound to an university, a alert should be shown."""
        response = self.client.get(self.url)
        self.assertIn(_(u"University with code <strong>%s</strong> does not exist.") % self.course.id.org,
                response.content.decode('utf-8'))


class TestAddTeachers(BaseCourseDetail):
    def test_add(self):
        response = self.client.get(self.url)  # call view to create the related fun course
        self.assertEqual(200, response.status_code)

        data = {
            'action': 'update-teachers',
            'teachers-TOTAL_FORMS': '2',
            'teachers-INITIAL_FORMS': '0',
            'teachers-MAX_NUM_FORMS': '5',
            'teachers-0-id': '',
            'teachers-0-order': 0,
            'teachers-0-full_name': "Mabuse",
            'teachers-0-title': "Doctor",
            'teachers-0-DELETE': False,
            'teachers-1-id': '',
            'teachers-1-order': 0,
            'teachers-1-DELETE': False,
            'teachers-1-full_name': "Who",
            'teachers-1-title': "Doctor",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(302, response.status_code)
        funcourse = Course.objects.get(key=self.course.id.to_deprecated_string())
        self.assertEqual(2, funcourse.teachers.count())


class TestDeleteTeachers(BaseCourseDetail):
    def test_delete(self):
        funcourse = Course.objects.create(key=self.course.id.to_deprecated_string())
        t1 = Teacher.objects.create(course=funcourse, full_name="Mabuse", title="Doctor")
        t2 = Teacher.objects.create(course=funcourse, full_name="Who", title="Doctor")
        self.assertEqual(2, funcourse.teachers.count())

        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertIn("Mabuse", response.content)
        data = {
            'action': 'update-teachers',
            'teachers-TOTAL_FORMS': '2',
            'teachers-INITIAL_FORMS': '2',
            'teachers-MAX_NUM_FORMS': '5',
            'teachers-0-id': t1.id,
            'teachers-0-order': 0,
            'teachers-0-full_name': "Mabuse",
            'teachers-0-title': "Doctor",
            'teachers-0-DELETE': True,
            'teachers-1-id': t2.id,
            'teachers-1-order': 0,
            'teachers-1-DELETE': False,
            'teachers-1-full_name': "Who",
            'teachers-1-title': "Doctor",
            }

        response = self.client.post(self.url, data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(1, funcourse.teachers.count())

class TestExportCoursesList(BaseBackoffice):

    def test_export(self):
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()
        self.login()

        response = self.client.post(self.list_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('text/csv', response._headers['content-type'][1])

        response_content = StringIO(response.content)
        data = [row for row in csv.reader(response_content)]

        self.assertEqual(2, len(data))
        course = data[1]
        self.assertEqual(self.university.code, course[2])
