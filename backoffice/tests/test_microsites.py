# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from student.tests.factories import UserFactory

from fun.tests.utils import skipUnlessLms, setMicrositeTestSettings

from ..models import Course

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


@skipUnlessLms
class TestMicrositeUsers(BaseCourseList):
    def setUp(self):
        super(TestMicrositeUsers, self).setUp()

        self.fcourse1 = Course.objects.create(key=self.course1.id, university=self.university)
        self.fcourse2 = Course.objects.create(key=self.course2.id, university=self.university)

        self.user0 = UserFactory(username='user0')
        self.user1 = MicrositeUserFactory(user__username='user1', site='microsite1').user
        self.user2 = MicrositeUserFactory(user__username='user2', site='microsite2').user

    @setMicrositeTestSettings(FAKE_MICROSITE1)
    def test_user_list_with_microsite1(self):
        response = self.client.get(reverse('backoffice:user-list'))
        users = response.context['users'].object_list
        self.assertTrue(self.user1 in users)
        self.assertTrue(self.user0 not in users)
        self.assertTrue(self.user2 not in users)

    @setMicrositeTestSettings(FAKE_MICROSITE2)
    def test_user_list_with_microsite2(self):
        response = self.client.get(reverse('backoffice:user-list'))
        users = response.context['users'].object_list
        self.assertTrue(self.user2 in users)
        self.assertTrue(self.user0 not in users)
        self.assertTrue(self.user1 not in users)

    @setMicrositeTestSettings(FAKE_MICROSITE1)
    def test_user_edit_with_microsite(self):
        response = self.client.get(reverse('backoffice:user-detail', args=[self.user1.username]))
        self.assertEqual(200, response.status_code)
        response = self.client.get(reverse('backoffice:user-detail', args=[self.user2.username]))
        self.assertEqual(404, response.status_code)
