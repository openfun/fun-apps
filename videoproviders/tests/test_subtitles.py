from collections import namedtuple
import os.path

from django.test import TestCase

from mock import patch

from . import fixtures
from videoproviders import subtitles

MockResponse = namedtuple('Response', ('status_code', 'content'))

class SubtitlesTests(TestCase):

    def setUp(self):
        subtitles.SUBTITLE_CACHE.clear()
        self.url = 'http://sub.com/sub.fr.srt'

    def get_fixture_content(self, file_name):
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', file_name)) as f:
            return f.read().decode('utf-8')

    @patch('requests.get')
    def test_get_vtt_content_from_srt_file(self, mock_get):
        mock_get.return_value = MockResponse(
            status_code=200,
            content=fixtures.get_content('sub.fr.srt')
        )
        vtt_content = subtitles.get_vtt_content(self.url)

        mock_get.assert_called_with(self.url)
        self.assertEqual(self.get_fixture_content('sub.fr.vtt'), vtt_content)

    @patch('requests.get')
    def test_vtt_content_is_cached(self, mock_get):
        mock_get.return_value = MockResponse(
            status_code=200,
            content=self.get_fixture_content('sub.fr.srt')
        )
        subtitles.get_vtt_content(self.url)
        subtitles.get_vtt_content(self.url)

        mock_get.assert_called_once_with(self.url)
