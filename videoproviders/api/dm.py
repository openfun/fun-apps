# -*- coding: utf-8 -*-
from datetime import datetime
import requests

from django.utils import formats

import dailymotion
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from .. import models


class Client(object):
    # Warning: this is mostly NOT unit-tested code

    VIDEO_FIELDS = 'id,created_time,duration,embed_url,published,publishing_progress,status,title,thumbnail_url'
    SUBTITLE_FIELDS = 'id,language,language_label,url'

    def __init__(self, course_key_string):
        self.course_module = self.get_course_module(course_key_string)
        self._dailymotion = None
        self._auth = None

    @staticmethod
    def get_course_module(course_key_string):
        course_key = CourseKey.from_string(course_key_string)
        return modulestore().get_course(course_key)

    @property
    def dailymotion(self):
        if self._dailymotion is None:
            self._dailymotion = dailymotion.Dailymotion()
            self._dailymotion.set_grant_type(
                'password', api_key=self.auth.api_key, api_secret=self.auth.api_secret,
                info={'username': self.auth.username, 'password': self.auth.password},
                scope=['userinfo', 'manage_videos', 'manage_subtitles']
            )
            self._dailymotion._session_store.set({
                'access_token': self.auth.access_token,
                'refresh_token': self.auth.refresh_token,
                'expires': self.auth.expires_at
            })
        return self._dailymotion

    @property
    def auth(self):
        """Return the DailymotionAuth credentials for the course after checking their validity."""
        if self._auth is None:
            try:
                auth = models.DailymotionAuth.objects.get_for_course(self.course_module)
            except models.DailymotionAuth.DoesNotExist:
                raise MissingCredentials(self.org)
            if not all([auth.username, auth.password, auth.api_key, auth.api_secret]):
                raise MissingCredentials()
            self._auth = auth
        return self._auth

    @property
    def playlist_id(self):
        """Playlist id associated to this account
        TODO"""

    @property
    def org(self):
        return self.course_module.location.org

    def get_videos(self):
        """Return a list of videos for the current user."""
        return list(self.iter_videos())

    def iter_videos(self):
        """Iterator over the current user's videos."""
        for result in self.iter_results("/me/videos", {'fields': self.VIDEO_FIELDS}):
            result['created_at'] = formats.date_format(
                datetime.fromtimestamp(result['created_time']),
                "DATETIME_FORMAT"
            )
            yield result

    def upload_file(self, file_object):
        """Upload a file using the Dailymotion storage service

        This can be used to store e.g: videos, subtitles or thumbnail files.

        Args:
            file_object: File-like object.

        Returns:
            url (str): url to the uploaded file.
        """
        # Get upload url
        upload_url = self.get_upload_url()['upload_url']

        # Store file using the obtained upload url
        upload_response = requests.post(
            upload_url,
            files={"file": file_object}
        )
        upload_response = upload_response.json()

        if 'url' not in upload_response:
            raise ClientError("Error in uploading file")

        return upload_response['url']

    def get_upload_url(self):
        """Get a URL for uploading a video.

        Returns: {
            "upload_url": ...
            "progress_url": ...
        }
        """
        response = self.get("/file/upload")
        if 'upload_url' not in response:
            raise ClientError("Could not fetch upload url")
        return response

    def get_video(self, video_id):
        return self.get("/video/{}".format(video_id), {
                            'fields': self.VIDEO_FIELDS,
                        })

    def update_video(self, video_id, **kwargs):
        """Set video attributes

        Returns:
            {
                "owner": "x1j661v",
                "id": video_id,
                "channel": None,
                "title": "My title"
            }
        """
        params = {}
        for key, value in kwargs.iteritems():
            if value is not None:
                if value == True:
                    value = "true"
                elif value == False:
                    value = "false"
                params[key] = value
        return self.post("/video/{}".format(video_id), params)

    def create_video(self, url, title=None):
        """Create a video after it has been uploaded.

        Returns: (same as update_video)
            {
                "owner": "x1j661v",
                "id": video_id,
                "channel": None,
                "title": "My title"
            }
        """
        params = {"url": url}
        if title:
            params["title"] = title
        return self.post("/me/videos", params)

    def delete_video(self, video_id):
        """Delete a video

        Note that the video may remain in the "deleted" status for some time.
        """
        return self.delete("/video/{}".format(video_id))

    def get_video_subtitles(self, video_id):
        """Get the subtitles associated to a video"""
        return list(self.iter_results("/video/{}/subtitles".format(video_id),
                                      {"fields": self.SUBTITLE_FIELDS}))

    def get_video_subtitle(self, video_id, subtitle_id):
        """Get a subtitle object"""
        return self.get(self.video_subtitle_url(video_id, subtitle_id),
                        {"fields": self.SUBTITLE_FIELDS})

    def delete_video_subtitle(self, video_id, subtitle_id):
        """Delete a subtitle"""
        return self.delete(self.video_subtitle_url(video_id, subtitle_id))

    def video_subtitle_url(self, video_id, subtitle_id):
        return "/video/{}/subtitles/{}".format(video_id, subtitle_id)

    def iter_results(self, url, params):
        """Iterate over the results of a GET request"""
        page = 1
        while True:
            params['page'] = page
            results = self.get(url, params)
            for result in results["list"]:
                yield result
            page += 1
            if not results['has_more']:
                break

    def get(self, endpoint, params=None):
        return self.call(endpoint, params=params)

    def post(self, endpoint, params=None, files=None):
        return self.call(endpoint, method='POST', params=params, files=files)

    def delete(self, endpoint, params=None):
        return self.call(endpoint, method='DELETE', params=params)

    def call(self, endpoint, method='GET', params=None, files=None):
        try:
            result = self.dailymotion.call(endpoint, method=method, params=params, files=files)
        except (dailymotion.DailymotionClientError, dailymotion.DailymotionApiError) as e:
            raise ClientError(e.message)

        self.auth.update_token(
            self.dailymotion._session_store.get_value("access_token"),
            self.dailymotion._session_store.get_value("refresh_token"),
            self.dailymotion._session_store.get_value("expires"),
        )
        return result


class MissingCredentials(Exception):
    pass

class ClientError(Exception):
    pass
