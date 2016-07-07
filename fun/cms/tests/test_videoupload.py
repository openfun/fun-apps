# -*- coding: utf-8 -*-
import json
from datetime import timedelta

from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.test.utils import override_settings

import mock

from courseware.tests.factories import InstructorFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from fun.tests.utils import skipUnlessCms
from videoproviders.api.base import ClientError
from videoproviders.models import VideoUploaderDeactivationPeriod


@skipUnlessCms
class TestVideoUpload(ModuleStoreTestCase):

    def setUp(self):
        super(TestVideoUpload, self).setUp(create_user=False)
        self.course = CourseFactory.create()
        self.instructor = InstructorFactory.create(course_key=self.course.id)
        self.client.login(username=self.instructor.username, password="test")

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

    @override_settings(LANGUAGE_CODE="en")
    def test_load_dashboard_in_deactivation_period(self):
        url = reverse("videoupload:home", kwargs={"course_key_string": self.course.id})

        # Create blocking period in the past
        VideoUploaderDeactivationPeriod.objects.create(
            start_time=now() - timedelta(days=1),
            end_time=now() - timedelta(days=2),
        )
        response_enabled = self.client.get(url)

        # Block dashboard
        VideoUploaderDeactivationPeriod.objects.update(
            end_time=now() + timedelta(days=1),
        )
        response_disabled = self.client.get(url)

        # Give instructor staff rights
        self.instructor.is_staff = True
        self.instructor.save()
        response_staff = self.client.get(url)

        disabled_string = "The video upload dashboard has been temporarily disabled"
        self.assertNotIn(disabled_string, response_enabled.content)
        self.assertIn(disabled_string, response_disabled.content)
        self.assertNotIn(disabled_string, response_staff.content)
