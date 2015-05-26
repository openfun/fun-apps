# -*- coding: utf-8 -*-

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from student.models import UserStanding
from student.tests.factories import UserFactory, CourseEnrollmentFactory, CourseAccessRoleFactory

from fun.tests.utils import skipUnlessLms
from ..models import Course
from .test_course_list import BaseCourseList


@skipUnlessLms
class TestUsers(BaseCourseList):
    def setUp(self):
        super(TestUsers, self).setUp()

        self.fcourse1 = Course.objects.create(key=self.course1.id, university=self.university)
        self.fcourse2 = Course.objects.create(key=self.course2.id, university=self.university)

        self.user2 = UserFactory(username='user1') # user with profile
        self.user3 = User.objects.create(username='user2')  # user without profile should not appear

    def test_user_list(self):
        response = self.client.get(reverse('backoffice:user-list'))
        self.assertEqual(200, response.status_code)
        self.assertTrue(self.user2 in response.context['users'])
        self.assertTrue(self.user in response.context['users'])
        self.assertTrue(self.user3 not in response.context['users'])

    def test_user_list_filtering(self):
        response = self.client.get(reverse('backoffice:user-list') + '?search=user1')
        self.assertEqual(200, response.status_code)
        self.assertTrue(self.user2 in response.context['users'])
        self.assertTrue(self.user3 not in response.context['users'])
        self.assertTrue(self.user not in response.context['users'])

    def test_user_detail(self):
        CourseEnrollmentFactory(course_id=self.course1.id, user=self.user2)
        CourseAccessRoleFactory(course_id=self.course1.id, user=self.user2, role=u'test_role')
        response = self.client.get(reverse('backoffice:user-detail', args=[self.user2.username]))
        self.assertEqual(200, response.status_code)

        self.assertEqual(response.context['enrollments'][0][0], self.course1.display_name)
        self.assertEqual(response.context['enrollments'][0][1].to_deprecated_string(),
                         self.course1.id.to_deprecated_string())
        self.assertEqual(response.context['enrollments'][0][2], False)
        self.assertEqual(set(response.context['enrollments'][0][3]), set([u'test_role']))

    def test_change_user_detail(self):
        data = {
            'email': u"change@example.com",
            'name': u"Néw näme",
            'gender': u"o",
            'language': u"Français",
            'level_of_education': u"other",
            'location': u"Paris",
            'year_of_birth': u"1973",
            'mailing_address': u"",
            'city': u"",
            'country': u"",
            'goals': u"fun",
        }
        response = self.client.post(reverse('backoffice:user-detail',
                args=[self.user2.username]), data)

        self.assertEqual(302, response.status_code)
        user = User.objects.select_related('profile').get(username=self.user2.username)
        self.assertEqual(u"change@example.com", user.email)
        self.assertEqual(u"Français", user.profile.language)

    def test_change_user_password(self):
        data = {
            'action': u"change-password",
            'new-password': u"new-password"
            }
        response = self.client.post(reverse('backoffice:user-detail',
                args=[self.user2.username]), data)
        self.assertEqual(302, response.status_code)
        self.assertEqual(self.user2, authenticate(username=self.user2.username, password='new-password'))

    def test_ban_user(self):
        data = {
            'action': u"ban-user",
            'value': u"disable"
            }
        response = self.client.post(reverse('backoffice:user-detail',
                args=[self.user2.username]), data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(UserStanding.objects.filter(user=self.user2,
                account_status=UserStanding.ACCOUNT_DISABLED).exists())

    def test_unban_user(self):
        UserStanding.objects.create(user=self.user2,
                account_status=UserStanding.ACCOUNT_DISABLED,
                changed_by=self.user)
        data = {
            'action': u"ban-user",
            'value': u"reenable"
            }
        response = self.client.post(reverse('backoffice:user-detail',
                args=[self.user2.username]), data)
        self.assertEqual(302, response.status_code)
        self.assertTrue(UserStanding.objects.filter(user=self.user2,
                account_status=UserStanding.ACCOUNT_ENABLED).exists())
