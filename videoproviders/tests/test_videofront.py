# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import ugettext_lazy as _
from mock import Mock, patch
import requests

from opaque_keys.edx.keys import CourseKey

from universities.tests.factories import UniversityFactory
from videoproviders.api import videofront
from videoproviders import models
from .fixtures import get_json_content


class UnauthenticatedVideofrontTests(TestCase):

    def test_missing_auth_token(self):
        client = videofront.Client("Org/Course/Run")
        self.assertRaises(videofront.MissingCredentials, client.get_auth)


class VideofrontGetAuthTests(TestCase):

    def setUp(self):
        self.course_key_string = "Org/Course/Run"
        UniversityFactory(code="Org")

    @override_settings(VIDEOFRONT_ADMIN_TOKEN='abcd')
    def test_automatic_user_creation(self):
        client = videofront.Client(self.course_key_string)
        response_404 = requests.Response()
        response_404.status_code = 404
        client.get = Mock(return_value=response_404)
        client.post = Mock(return_value=Mock(json=Mock(return_value={
            'username': 'Org',
            'token': 'tokenvalue'
        })))

        self.assertEqual('tokenvalue', client.get_auth())
        self.assertEqual('tokenvalue', models.VideofrontAuth.objects.get().token)

    @patch('requests.get')
    def test_request_with_token(self, mock_get):
        client = videofront.Client(self.course_key_string)
        client.get_auth = Mock(side_effect=ValueError('this method should not be called'))
        response_200 = requests.Response()
        response_200.status_code = 200
        mock_get.return_value = response_200

        client.request('endpoint', 'GET', token="newtoken")

        mock_get.assert_called_once_with(
            'https://video.alt.openfun.fr/api/v1/endpoint',
            headers={'Authorization': 'Token newtoken'},
            timeout=10
        )


class VideofrontTests(TestCase):

    def setUp(self):
        self.course_key_string = "Org/Course/Run"
        university = UniversityFactory(code="Org")
        models.VideofrontAuth.objects.create(university=university, token="abcdefgh")

    @property
    def course_id(self):
        return CourseKey.from_string(self.course_key_string)

    def test_auth_token(self):
        client = videofront.Client(self.course_key_string)
        self.assertEqual('abcdefgh', client.get_auth())

    def test_get_video(self):
        client = videofront.Client(self.course_key_string)
        client.get = Mock(return_value=Mock(
            json=Mock(return_value=get_json_content('videofront/video_success.json'))
        ))

        video = client.get_video('videoid')

        self.assertEqual('videoid', video['id'])
        self.assertEqual("Dramatic Chipmunk.mp4", video['title'])
        self.assertEqual(u"18 août 2016 07:29:47", video['created_at'])
        self.assertEqual(1471498187.0, video['created_at_timestamp'])
        self.assertEqual(3, len(video['video_sources']))

    def test_get_video_with_subtitles(self):
        client = videofront.Client(self.course_key_string)
        client.get = Mock(return_value=Mock(
            json=Mock(return_value=get_json_content('videofront/video_success.json'))
        ))

        video = client.get_video_with_subtitles('videoid')

        self.assertIn('subtitles', video)
        self.assertEqual(1, len(video['subtitles']))
        self.assertEqual('subsid', video['subtitles'][0]['id'])
        self.assertEqual('bg', video['subtitles'][0]['language'])
        self.assertEqual(_('Bulgarian'), video['subtitles'][0]['language_label'])

    def test_playlist_id_with_existing_playlist(self):
        models.VideofrontCourseSettings.objects.create(course_id=self.course_id, playlist_id='playlistid')
        client = videofront.Client(self.course_key_string)
        self.assertEqual('playlistid', client.playlist_id)

    def test_playlist_id_with_missing_playlist(self):
        client = videofront.Client(self.course_key_string)
        client.get = Mock(return_value=Mock(
            json=Mock(return_value=[])
        ))
        client.post = Mock(return_value=Mock(
            json=Mock(return_value=get_json_content('videofront/playlist_created.json'))
        ))

        playlist_id = client.playlist_id

        self.assertEqual('playlistid', playlist_id)
        client.get.assert_called_once()
        client.post.assert_called_once()
        self.assertEqual(1, models.VideofrontCourseSettings.objects.count())
        self.assertEqual('playlistid', models.VideofrontCourseSettings.objects.get().playlist_id)
