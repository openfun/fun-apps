# -*- coding: utf-8 -*-

import csv
from StringIO import StringIO

from django.contrib.auth.models import User, Group
from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory, CourseAboutFactory, ABOUT_ATTRIBUTES

from student.models import UserProfile
from universities.factories import UniversityFactory

from ..views import get_about_sections


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


class TestDailymotionIDRetrieving(BaseCourseList):
    """Test that our dailymotion ID is correctly extracted from course about section which is
    made to store youtube ID. We copy/paste those 2 functions because we can't import
    cms/djangoapps/models/settings/course_details.py but it reduce the scope of the test...
    """
    def _recompose_video_tag(self, video_key):
        result = None
        if video_key:
            result = '<iframe width="560" height="315" src="//www.youtube.com/embed/' + \
                video_key + '?rel=0" frameborder="0" allowfullscreen=""></iframe>'
        return result
    def _update_about_item(self, course_key, about_key, data, course, user):
        temploc = course_key.make_usage_key('about', about_key)
        store = modulestore()
        if data is None:
            try:
                store.delete_item(temploc, user.id)
            except ValueError:
                pass
        else:
            try:
                about_item = store.get_item(temploc)
            except ItemNotFoundError:
                about_item = store.create_xblock(course.runtime, course.id, 'about', about_key)
            about_item.data = data
            store.update_item(about_item, user.id, allow_not_found=True)

    def test_dailymotion_extraction(self):
        DM_CODE = 'x2an9mg'
        module_store = modulestore()
        descriptor = module_store.get_course(self.course2.id)
        recomposed_video_tag = self._recompose_video_tag(DM_CODE)
        self._update_about_item(self.course2.id, 'video', recomposed_video_tag, descriptor, self.user)

        course_infos = get_about_sections(descriptor)

        self.assertEqual(DM_CODE, course_infos['video'])
