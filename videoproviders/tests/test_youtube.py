# -*- coding: utf-8 -*-
import json
import mock
import tempfile

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from courseware.tests.factories import InstructorFactory
from opaque_keys.edx.keys import CourseKey

from fun.tests.utils import skipUnlessCms
from universities.tests.factories import UniversityFactory
from videoproviders.api.youtube import MissingCredentials, Client
from videoproviders.models import YoutubeAuth, YoutubeCourseSettings

from . import fixtures


def mock_list_service(execute_return_value):
    return mock.Mock(return_value=MockResource('list', execute_return_value))
def mock_download_service(execute_return_value):
    return mock.Mock(return_value=MockResource('download', execute_return_value))
def mock_insert_service(execute_return_value):
    return mock.Mock(return_value=MockResource('insert', execute_return_value))

class MockResource(object):
    """
    Mock youtube service class that exposes a 'method_name' method.
    """
    def __init__(self, method_name, execute_return_value):
        setattr(self, method_name, mock.Mock(**{
            'return_value': mock.Mock(**{
                'execute.return_value': execute_return_value
            })
        }))


@mock.patch('apiclient.discovery.build', new=mock.Mock)
class BaseYoutubeTestCase(TestCase):
    """
    Youtube test classes should inherit from this class, or use the same
    decorator to patch the youtube service, so that no real call to the Youtube
    API is ever made.
    """

    def setUp(self):
        self.course_key_string = "org/coursename/run"
        self.youtube_client = Client(self.course_key_string)

    @property
    def course_id(self):
        return CourseKey.from_string(self.course_key_string)

    def create_credentials(self):
        university = UniversityFactory(code="org")
        YoutubeAuth.objects.create(
            university=university,
            client_id="clientid",
            client_secret="clientsecret",
            access_token="accesstoken",
            refresh_token="refreshtoken"
        )

    def create_course_settings(self):
        return YoutubeCourseSettings.objects.create(
            playlist_id="playlistid1",
            course_id=CourseKey.from_string(self.course_key_string)
        )


class YoutubeWithoutCredentialsTests(BaseYoutubeTestCase):

    def test_missing_credentials_in_database(self):
        self.assertRaises(MissingCredentials, getattr, self.youtube_client, "credentials")


class YoutubeTests(BaseYoutubeTestCase):

    def setUp(self):
        super(YoutubeTests, self).setUp()
        self.create_credentials()

    def test_playlist_id_is_found(self):
        playlist_id = "correctplaylistid"
        self.youtube_client.auth.playlists = mock_list_service({
            "items": [
                {
                    "id": "wrongplaylistid",
                    "snippet": {
                        "title": "some title",
                    }
                },
                {
                    "id": playlist_id,
                    "snippet": {
                        "title": self.youtube_client.course_key_string
                    }
                }
            ]
        })

        self.assertEqual(0, YoutubeCourseSettings.objects.count())
        self.assertEqual(playlist_id, self.youtube_client.playlist_id)
        self.assertEqual(playlist_id, YoutubeCourseSettings.objects.get().playlist_id)

    def test_iter_videos_for_empty_course(self):
        self.create_course_settings()
        self.youtube_client.auth.playlistItems = mock_list_service({"items": []})
        videos = list(self.youtube_client.iter_videos())
        self.assertEqual([], videos)

    def test_iter_videos(self):
        settings = self.create_course_settings()
        self.youtube_client.auth.playlistItems = mock_list_service(fixtures.get_json_content(
            "youtube/playlist_items1.json"
        ))
        self.youtube_client.auth.videos = mock_list_service(fixtures.get_json_content(
            "youtube/video1.json"
        ))
        videos = list(self.youtube_client.iter_videos())
        self.youtube_client.auth.playlistItems.return_value.list.assert_called_with(
            playlistId=settings.playlist_id,
            part="id,snippet",
            pageToken=None,
            maxResults=50
        )
        self.assertEqual(1, len(videos))
        self.assertEqual("videoid1", videos[0]["id"])
        self.assertEqual("Video title 1", videos[0]["title"])
        self.assertEqual("4 juillet 2016 13:12:12", videos[0]["created_at"])

    def test_generate_subtitle_name(self):
        self.youtube_client.auth.captions = mock_list_service({
            "items": [
               {
                    "snippet": {
                        "language": "pl",
                        "name": "",
                    }
                },
                {
                    "snippet": {
                        "language": "fr",
                        "name": "",
                    }
                },
                {
                    "snippet": {
                        "language": "fr",
                        "name": "#2",
                    }
                },
                {
                    "snippet": {
                        "language": "en",
                        "name": "#1",
                    }
                },
            ]
        })
        self.assertEqual("", self.youtube_client.find_next_subtitle_name("videoid1", "dk"))
        self.assertEqual("#1", self.youtube_client.find_next_subtitle_name("videoid1", "pl"))
        self.assertEqual("#3", self.youtube_client.find_next_subtitle_name("videoid1", "fr"))
        self.assertEqual("#2", self.youtube_client.find_next_subtitle_name("videoid1", "en"))


@skipUnlessCms
class YoutubeCmsTests(BaseYoutubeTestCase):
    """
    This test case covers the CMS views. Technically, these tests could be
    located in fun/cms, but then it would have to import lots of code from this
    module.
    """
    def setUp(self):
        super(YoutubeCmsTests, self).setUp()
        self.create_credentials()
        self.instructor = InstructorFactory.create(course_key=self.course_id)
        self.client.login(username=self.instructor.username, password="test")

        self.subtitle_id = "subtitleid"
        self.youtube_client.auth.captions = mock_list_service({
            "items": [{
                "id": self.subtitle_id,
                "snippet": {
                    "language": "fr"
                }
            }]
        })
        self.subtitle_download_url = reverse(
            "youtube:download_subtitle",
            kwargs={'subtitle_id': self.subtitle_id, 'course_key_string': self.course_key_string}
        )

    @override_settings(CMS_BASE="yipikaye.com")
    def test_iter_subtitles(self):
        subtitles = list(self.youtube_client.iter_subtitles("somevideoid"))

        self.assertEqual(1, len(subtitles))
        subtitle = subtitles[0]
        expected_url = "//yipikaye.com" + self.subtitle_download_url

        self.assertEqual("subtitleid", subtitle["id"])
        self.assertEqual("fr", subtitle["language"])
        self.assertEqual(expected_url, subtitle["url"])

    def test_download_subtitle(self):
        self.youtube_client.auth.captions = mock_download_service("vtt content here")
        self.assertEqual("vtt content here", self.youtube_client.download_subtitle(self.subtitle_id))

    @mock.patch('videoproviders.api.youtube.Client.download_subtitle')
    def test_download_subtitle_view(self, mock_download_subtitle):
        mock_download_subtitle.return_value = "vtt content here"
        response = self.client.get(self.subtitle_download_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual("vtt content here", response.content)

    def test_get_upload_url(self):
        upload_url = self.youtube_client.get_upload_url()
        expected_url = reverse("youtube:upload_video", kwargs={'course_key_string': self.course_key_string})
        self.assertEqual(expected_url, upload_url["url"])
        self.assertEqual("path", upload_url["file_parameter_name"])

    def test_upload_video(self):
        self.create_course_settings()
        video_file = tempfile.NamedTemporaryFile(prefix="test_youtube_video", suffix=".mp4")

        # Upload video
        self.youtube_client.auth.videos = mock_insert_service({
            "id": "videoid1"
        })
        self.youtube_client.auth.playlistItems = mock_insert_service({})
        video = self.youtube_client.upload_video(video_file)

        # Create video
        self.youtube_client.auth.videos = mock_list_service(fixtures.get_json_content(
            "youtube/video1.json"
        ))
        created_video = self.youtube_client.create_video(video)

        self.assertEqual({"id": "videoid1"}, video)
        self.assertEqual("videoid1", created_video["id"])

    @mock.patch('videoproviders.api.youtube.Client.upload_video')
    def test_upload_video_view(self, mock_upload_video):
        mock_upload_video.return_value = {"id": "videoid1"}
        video_file = tempfile.NamedTemporaryFile(prefix="test_youtube_video", suffix=".mp4")
        url = reverse("youtube:upload_video", kwargs={"course_key_string": self.course_key_string})

        # This is how a file is uploaded in django tests
        upload_response = self.client.post(url, {
            "name": video_file.name,
            Client.FILE_PARAMETER_NAME: video_file
        })

        self.assertEqual(200, upload_response.status_code)
        self.assertEqual({"id": "videoid1"}, json.loads(upload_response.content))
