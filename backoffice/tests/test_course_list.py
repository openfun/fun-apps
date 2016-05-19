# -*- coding: utf-8 -*-

import csv
from StringIO import StringIO

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

from course_modes.models import CourseMode
from student.tests.factories import CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, CourseAboutFactory, ABOUT_ATTRIBUTES

from fun.tests.utils import skipUnlessLms
from student.models import UserProfile
from universities.tests.factories import UniversityFactory

from ..utils import get_course_modes
from ..utils import get_enrollment_mode_count


@skipUnlessLms
class BaseCourseList(ModuleStoreTestCase):
    def setUp(self):
        super(BaseCourseList, self).setUp(create_user=False)
        self.user = User.objects.create(username='backoffice', is_staff=True)
        self.user.set_password('password')
        self.user.save()
        self.backoffice_group, _created = Group.objects.get_or_create(name='fun_backoffice')
        self.user.groups.add(self.backoffice_group)
        UserProfile.objects.create(user=self.user)
        self.client.login(username=self.user.username, password='password')

        self.university = UniversityFactory.create()
        self.course1 = CourseFactory.create(number='001', display_name=u"unpublished",
                                            ispublic=False, org=self.university.code)

        CourseAboutFactory.create(course_id=self.course1.id,
                                  course_runtime=self.course1.runtime)

        self.course2 = CourseFactory.create(org=self.university.code, number='002',
                             display_name=u"published", ispublic=True)
        self.list_url = reverse('backoffice:courses-list')


class VerifiedCourseList(BaseCourseList):
    def setUp(self):
        super(VerifiedCourseList, self).setUp()
        CourseMode.objects.create(course_id=self.course1.id, mode_slug='honor', mode_display_name=u"honor")
        CourseMode.objects.create(course_id=self.course1.id, mode_slug='verified', mode_display_name=u"verified")
        CourseEnrollmentFactory(course_id=self.course1.id, mode='honor')

        self.course3 = CourseFactory.create(org=self.university.code, number='003',
                             display_name=u"published", ispublic=True)
        CourseMode.objects.create(course_id=self.course3.id, mode_slug='honor', mode_display_name=u"honor")
        CourseMode.objects.create(course_id=self.course3.id, mode_slug='verified', mode_display_name=u"verified")
        CourseEnrollmentFactory(course_id=self.course3.id, mode='honor')


class TestExportCoursesList(BaseCourseList):
    def get_csv_response_rows(self, response):
        response_content = StringIO(response.content)
        response_content.seek(0)
        return [row for row in csv.reader(response_content)]

    def test_export(self):
        response = self.client.post(self.list_url)
        self.assertEqual('text/csv', response._headers['content-type'][1])
        rows = self.get_csv_response_rows(response)
        self.assertEqual(3, len(rows))
        course = rows[1]
        self.assertIn("www.youtube.com/embed/testing-video-link", course)
        self.assertIn(ABOUT_ATTRIBUTES['effort'], course)


class TestCoursesModeUtils(VerifiedCourseList):
    def test_get_course_modes(self):
        course_modes = get_course_modes()
        self.assertIn(unicode(self.course1.id), course_modes)
        self.assertNotIn(unicode(self.course2.id), course_modes)
        self.assertEqual(set(['verified', 'honor']),
                set(course_modes[unicode(self.course1.id)]))

    def test_get_enrollment_mode_count(self):
        mode_count = get_enrollment_mode_count(self.course2.id)
        self.assertEqual({}, mode_count)

        mode_count = get_enrollment_mode_count(self.course1.id)
        self.assertEqual({'honor': 1, 'verified': 0}, mode_count)

        CourseEnrollmentFactory(course_id=self.course1.id, mode='verified')
        mode_count = get_enrollment_mode_count(self.course1.id)
        self.assertEqual({'honor': 1, 'verified': 1}, mode_count)
