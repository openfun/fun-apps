# -*- coding: utf-8 -*-

import csv
from StringIO import StringIO

from bs4 import BeautifulSoup
import mock

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.utils.translation import ugettext as _

from lang_pref import LANGUAGE_KEY
from openedx.core.djangoapps.user_api.preferences.api import set_user_preference
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.tests.factories import CourseFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from courseware.tests.factories import StaffFactory, InstructorFactory
from student.models import UserProfile

from backoffice.views import courses_views
from courses.models import Course
from courses.tests.factories import CourseUniversityRelationFactory, CourseFactory as FunCourseFactory
from fun.tests.utils import skipUnlessLms
from universities.tests.factories import UniversityFactory


@skipUnlessLms
class BaseTestCase(ModuleStoreTestCase):
    def setUp(self):
        self.password = super(BaseTestCase, self).setUp()
        self.course = None
        self.backoffice_group = None

    def init(self, is_superuser, university_code=None):
        self.backoffice_group, _created = Group.objects.get_or_create(name='fun_backoffice')
        self.user.is_staff = False
        self.user.is_superuser = is_superuser
        self.user.save()
        UserProfile.objects.create(user=self.user)
        self.course = CourseFactory.create(org=university_code)

        self.fun_course = FunCourseFactory.create(key=unicode(self.course.scope_ids.usage_id.course_key))
        if university_code:
            self.university = UniversityFactory.create(slug=university_code, code=university_code)
            CourseUniversityRelationFactory(course=self.fun_course, university=self.university)

    def login(self):
        self.client.login(username=self.user.username, password=self.password)


class BaseBackoffice(BaseTestCase):
    def setUp(self):
        super(BaseBackoffice, self).setUp()
        self.init(False, 'fun')
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
        self.url = reverse('backoffice:course-detail', args=[unicode(self.course.scope_ids.usage_id.course_key)])


class TestAuthentication(BaseBackoffice):
    def test_non_logged_in_users_should_not_access_the_backoffice(self):
        self.client.logout()
        response = self.client.get(self.list_url, follow=True)
        # Verify there is only one redirect to the login page
        self.assertEqual(1, len(response.redirect_chain))
        self.assertEqual(302, response.redirect_chain[0][1])
        self.assertEqual("http://testserver" + reverse('signin_user') + "?next={}".format(self.list_url),
                         response.redirect_chain[0][0])

    def test_users_not_belonging_to_group_should_not_login(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.list_url, follow=True)
        # Users that have already logged-in should not be redirected to the
        # login page; instead, they should see a 404 page.
        self.assertEqual(404, response.status_code)

    def test_staff_users_see_all_courses(self):
        self.user.groups.add(self.backoffice_group)
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.list_url)
        self.assertEqual(1, len(response.context['course_infos']))


@override_settings(COURSE_SIGNALS_DISABLED=False)
class TestGenerateCertificate(BaseBackoffice):
    def setUp(self):
        super(TestGenerateCertificate, self).setUp()
        self.login_with_backoffice_group()

    def test_certificate(self):
        url = reverse('backoffice:generate-test-certificate', args=[unicode(self.course.scope_ids.usage_id.course_key)])
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        data = {
            'full_name': u'super élève',
        }
        response = self.client.post(url, data)
        self.assertEqual('application/pdf', response._headers['content-type'][1])


class TestDeleteCourse(BaseCourseDetail):
    def test_get_view(self):
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)

    def test_funcourse_automatique_creation(self):
        """A fun Course object should be automaticaly created if it does not already exist."""
        response = self.client.get(self.url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, Course.objects.filter(key=unicode(self.course.scope_ids.usage_id.course_key)).count())

    def test_delete_course(self):
        courses_views.logger.warning = mock.Mock()
        data = {'action': 'delete-course'}
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(None, modulestore().get_course(self.course.id))
        self.assertEqual(0, Course.objects.filter(key=unicode(self.course.scope_ids.usage_id.course_key)).count())
        self.assertIn(_(u"Course <strong>%s</strong> has been deleted.") % self.course.id,
                      response.content.decode('utf-8'))
        self.assertEqual(1, courses_views.logger.warning.call_count)

    def test_no_university(self):
        """In a course is not bound to an university, a alert should be shown."""
        response = self.client.get(self.url)
        self.assertIn(_(u"University with code <strong>%s</strong> does not exist.") % self.course.id.org,
                      response.content.decode('utf-8'))


class TestRenderRoles(BaseCourseDetail):
    def setUp(self):
        super(TestRenderRoles, self).setUp()
        InstructorFactory(course_key=self.course.id, username='instructor_robot1')
        StaffFactory(course_key=self.course.id, username='staff_robot')
        InstructorFactory(course_key=self.course.id, username='instructor_robot2')

    def test_render_roles(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content)
        roles = soup.find_all(class_='role-name')
        self.assertEqual([role.text[:-1] for role in roles],
                         ['instructor', 'staff'])

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
