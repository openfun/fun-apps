# -*- coding: utf-8 -*-
import lxml.etree
from mock import patch

from django.test import TestCase

from . import fixtures
from videoproviders.api import libcast


class LibcastTests(TestCase):

    def setUp(self):
        self.course_key_string = "Org/Course/Run"
        self.resource_slug = "video-bienvenue-sur-fun"
        self.subtitle_id = "ceciestunidentifiantde40characteresetoui.fr.srt"
        libcast.CachedResource.CACHE.clear()

    @patch('videoproviders.subtitles.get_vtt_content')
    def test_get_vtt_content(self, mock_get_vtt_content):
        mock_get_vtt_content.return_value = 'some random content'
        expected_url = 'https://fun.libcast.com/resource/{}/subtitles/{}'.format(self.resource_slug, self.subtitle_id)

        vtt_content = libcast.get_vtt_content(self.course_key_string, self.resource_slug, self.subtitle_id)

        self.assertEqual(mock_get_vtt_content.return_value, vtt_content)
        mock_get_vtt_content.assert_called_once_with(expected_url)

    @patch('videoproviders.api.libcast.Client.get_resource')
    def test_get_resource_dict(self, mock_get_resource):
        resource_content = fixtures.get_content('libcast/resource.xml').encode('utf-8')
        mock_get_resource.return_value = lxml.etree.fromstring(resource_content)
        resource = libcast.get_resource_dict(self.course_key_string, self.resource_slug)

        mock_get_resource.assert_called_once_with(self.resource_slug)

        self.assertIsNotNone(resource)
        self.assertEqual([{
            "id": "ff60214f3698f1b55ae593fab4996ffc5afc72ca.fr.srt",
            "language": "fr",
            "language_label": u"Français",
            "url": ("https://fun.libcast.com/resource/video-bienvenue-sur-fun/subtitles/"
                    "ff60214f3698f1b55ae593fab4996ffc5afc72ca.fr.srt"),
        }], resource['subtitles'])

        self.assertEqual(3, len(resource['downloadable_files']))
        self.assertIn("url", resource['downloadable_files'][0])
        self.assertIn("name", resource['downloadable_files'][0])
        self.assertEqual(
            "https://fun.libcast.com/resource/video-bienvenue-sur-fun/flavor/video/fun-hd.mp4",
            resource['downloadable_files'][0]['url']
        )

    @patch('videoproviders.api.libcast.get_resource_dict')
    def test_get_cached_resource_dict(self, mock_get_resource_dict):
        resource_dict = {"key": "value"}
        mock_get_resource_dict.return_value = resource_dict
        resource_1 = libcast.get_cached_resource_dict(self.course_key_string, self.resource_slug)
        resource_2 = libcast.get_cached_resource_dict(self.course_key_string, self.resource_slug)

        mock_get_resource_dict.assert_called_once_with(self.course_key_string, self.resource_slug)
        self.assertEqual(resource_dict, resource_1)
        self.assertEqual(resource_1, resource_2)


class SelfExpiringLockTests(TestCase):

    def setUp(self):
        self.cache = libcast.get_cache("default")

    def test_lock_deletes_cache_key_on_exit(self):
        key = "test_lock_deletes_cache_key_on_exit"
        self.cache.delete(key)
        with libcast.SelfExpiringLock(key, 1):
            value_inside_lock = self.cache.get(key)
        value_outside_lock = self.cache.get(key)

        self.assertEqual(1, value_inside_lock)
        self.assertIsNone(value_outside_lock)

    def test_lock_raises_error_if_waiting_for_too_long(self):
        key = "test_lock_raises_error_if_waiting_for_too_long"
        timeout = 0.001
        self.cache.set(key, 1, timeout=1000*timeout)
        self.assertRaises(ValueError, self.wait_for_lock, key, timeout)

    def wait_for_lock(self, key, timeout):
        with libcast.SelfExpiringLock(key, timeout):
            pass


class LibcastCachedResourceTests(TestCase):

    def test_get_set_delete(self):
        course_key_string = "org/num/run"
        video_id = "video_id"
        content = {"key": "value"}
        cached = libcast.CachedResource(course_key_string, video_id)

        version_1 = cached.get()
        cached.set(content)
        version_2 = cached.get()
        cached.expire()
        version_3 = cached.get()

        self.assertIsNone(version_1)
        self.assertEqual(content, version_2)
        self.assertIsNone(version_3)
