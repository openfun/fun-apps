# -*- coding: utf-8 -*-

import csv
from StringIO import StringIO

from django.contrib.auth.models import User, Group
from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.django_utils import TEST_DATA_MOCK_MODULESTORE
from xmodule.modulestore.tests.factories import CourseFactory

from student.models import UserProfile
from universities.factories import UniversityFactory


DM_CODE = 'x2an9mg'
YOUTUBE_IFRAME = """\n\n\n<iframe width="560" height="315" src="//www.youtube.com/embed/%s?rel=0" frameborder="0" allowfullscreen=""></iframe>\n\n\n""" % DM_CODE



class BaseCourseList(ModuleStoreTestCase):
    def setUp(self):
        super(BaseCourseList, self).setUp(create_user=False)
        self.user = User.objects.create(username='backoffice', is_staff=True)
        self.user.set_password('password')
        self.user.save()
        self.backoffice_group, created = Group.objects.get_or_create(name='fun_backoffice')
        self.user.groups.add(self.backoffice_group)
        UserProfile.objects.create(user=self.user)
        self.client.login(username=self.user.username, password='password')

        self.university = UniversityFactory.create()

        self.course1 = CourseFactory.create(number='001', display_name=u"unpublished", ispublic=False,
                video=YOUTUBE_IFRAME, effort = '3h00')
        self.course2 = CourseFactory.create(org=self.university.code, number='002',
                display_name=u"unpublished", ispublic=True,
                video=YOUTUBE_IFRAME, effort = '3h00')
        self.list_url = reverse('backoffice:courses-list')

#@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
#class TestCoursesList(BaseBackoffice):
#    def test_courselist(self):
#        #import ipdb; ipdb.set_trace()
#        pass



@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class TestExportCoursesList(BaseCourseList):
    def get_csv_response_rows(self, response):
        response_content = StringIO(response.content)
        response_content.seek(0)
        return [row for row in csv.reader(response_content)]

    def test_export(self):

        response = self.client.post(self.list_url)
        self.assertEqual('text/csv', response._headers['content-type'][1])
        import ipdb; ipdb.set_trace()
        rows = self.get_csv_response_rows(response)
        self.assertEqual(2, len(rows))

        course = rows[1]
        self.assertIn(DM_CODE, course)
        self.assertIn('3h00', course)
