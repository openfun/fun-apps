# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from courses.models import Course
from fun.tests.utils import skipUnlessLms, setMicrositeTestSettings

from .factories import MicrositeUserFactory
from .test_course_list import BaseCourseList


FAKE_MICROSITE1 = {
    "SITE_NAME": "microsite1",
    "university": "organization1",
    "course_org_filter": "org1",
    }

FAKE_MICROSITE2 = {
    "SITE_NAME": "microsite2",
    "university": "organization2",
    "course_org_filter": "org2",
    }


class BaseMicrositeTestCase(ModuleStoreTestCase):
    def _create_user(self, username, microsite):
        """Create a user to log in the backoffice belonging to the given microsite."""
        user = MicrositeUserFactory(user__username=username, site=microsite).user
        user.set_password('password')
        user.save()
        backoffice_group, created = Group.objects.get_or_create(name='fun_backoffice')
        user.groups.add(backoffice_group)
        return user

    def setUp(self):
        super(BaseMicrositeTestCase, self).setUp(create_user=False)
        self.backuser1 = self._create_user('backuser1', 'microsite1')
        self.backuser2 = self._create_user('backuser2', 'microsite2')


@skipUnlessLms
class TestMicrositeUsers(BaseMicrositeTestCase):
    def setUp(self):
        super(TestMicrositeUsers, self).setUp()

        self.user0 = UserFactory(username='user0')
        self.user1 = MicrositeUserFactory(user__username='user1', site='microsite1').user
        self.user2 = MicrositeUserFactory(user__username='user2', site='microsite2').user

    @setMicrositeTestSettings(FAKE_MICROSITE1)
    def test_user_list_with_microsite1(self):
        self.client.login(username=self.backuser1.username, password='password')
        response = self.client.get(reverse('backoffice:user-list'))
        users = response.context['users'].object_list
        self.assertTrue(self.user1 in users)
        self.assertTrue(self.user0 not in users)
        self.assertTrue(self.user2 not in users)

    @setMicrositeTestSettings(FAKE_MICROSITE2)
    def test_user_list_with_microsite2(self):
        self.client.login(username=self.backuser2.username, password='password')
        response = self.client.get(reverse('backoffice:user-list'))
        users = response.context['users'].object_list
        self.assertTrue(self.user2 in users)
        self.assertTrue(self.user0 not in users)
        self.assertTrue(self.user1 not in users)

    @setMicrositeTestSettings(FAKE_MICROSITE1)
    def test_user_edit_with_microsite(self):
        self.client.login(username=self.backuser1.username, password='password')
        response = self.client.get(reverse('backoffice:user-detail', args=[self.user1.username]))
        self.assertEqual(200, response.status_code)
        response = self.client.get(reverse('backoffice:user-detail', args=[self.user2.username]))
        self.assertEqual(404, response.status_code)

    @setMicrositeTestSettings(FAKE_MICROSITE1)
    def test_microsite_acces_controle(self):
        """Backoffice user from microsite1 should not acces to microsite2 backoffice."""
        self.client.login(username=self.backuser2.username, password='password')
        response = self.client.get(reverse('backoffice:user-list'))
        self.assertEqual(302, response.status_code)  # should be redirected to login page
