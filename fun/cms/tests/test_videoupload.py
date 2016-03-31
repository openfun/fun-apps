# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import reverse

import mock

from courseware.tests.factories import InstructorFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from fun.tests.utils import skipUnlessCms
from videoproviders.api.base import ClientError


@skipUnlessCms
class TestVideoUpload(ModuleStoreTestCase):

    def setUp(self):
        super(TestVideoUpload, self).setUp(create_user=False)
        self.course = CourseFactory.create()
        instructor = InstructorFactory.create(course_key=self.course.id)
        self.client.login(username=instructor.username, password="test")

    def test_api_videos_with_no_university(self):
        url = reverse("videoupload:videos", kwargs={"course_key_string": self.course.id})
        response = self.client.get(url)
        data = json.loads(response.content)

        self.assertIn("error", data)

    @mock.patch("videoproviders.api.libcast.Client.update_video_title")
    def test_failing_video_title_change(self, mock_update_video_title):
        mock_update_video_title.side_effect = ClientError(u"dummy error")
        response = self.client.post(reverse("videoupload:video", kwargs={
            "course_key_string": self.course.id, "video_id": "dummy_video_id"
        }))
        data = json.loads(response.content)

        self.assertIn("error", data)
        self.assertEqual(u'Impossible de changer le titre de la vidéo : dummy error', data["error"])
