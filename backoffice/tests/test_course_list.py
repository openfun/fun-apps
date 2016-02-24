# -*- coding: utf-8 -*-

import csv
from StringIO import StringIO

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, CourseAboutFactory, ABOUT_ATTRIBUTES

from fun.tests.utils import skipUnlessLms
from student.models import UserProfile
from universities.tests.factories import UniversityFactory


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
                                            ispublic=False)

        CourseAboutFactory.create(course_id=self.course1.id,
                                  course_runtime=self.course1.runtime)

        self.course2 = CourseFactory.create(org=self.university.code, number='002',
                             display_name=u"published", ispublic=True)
        self.list_url = reverse('backoffice:courses-list')

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
