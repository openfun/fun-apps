import logging
import os.path

from django.test import TestCase
from django.test.utils import override_settings

from mock import patch, Mock

from . import fixtures
from videoproviders import subtitles


class SubtitlesTests(TestCase):

    def setUp(self):
        subtitles.SUBTITLE_CACHE.clear()
        self.url = 'http://sub.com/sub.fr.srt'

    def get_fixture_content(self, file_name):
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', file_name)) as f:
            return f.read()

    @patch('requests.get')
    def test_get_vtt_content_from_srt_file(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            iter_content=Mock(return_value=fixtures.get_content('sub.fr.srt'))
        )
        vtt_content = subtitles.get_vtt_content(self.url)

        mock_get.assert_called_once_with(self.url, stream=True)
        self.assertEqual(self.get_fixture_content('sub.fr.vtt').decode("utf-8"), vtt_content)

    @patch('requests.get')
    def test_vtt_content_is_cached(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            iter_content=Mock(return_value=self.get_fixture_content('sub.fr.srt'))
        )
        subtitles.get_vtt_content(self.url)
        subtitles.get_vtt_content(self.url)

        mock_get.assert_called_once_with(self.url, stream=True)

    @override_settings(SUBTITLES_MAX_BYTES=10)
    @patch('requests.get')
    def test_large_vtt_content_is_not_loaded(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            iter_content=Mock(return_value=self.get_fixture_content('sub.fr.srt'))
        )
        subtitles.logger.setLevel(logging.FATAL)

        self.assertIsNone(subtitles.get_vtt_content(self.url))
        mock_get.assert_called_once_with(self.url, stream=True)
        self.assertEqual("", subtitles.SUBTITLE_CACHE.get(self.url))
